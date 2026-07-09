# app/services/transaction_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, or_
from fastapi import HTTPException, status
from app.models.transaction import Transaction, TransactionType
from app.models.category import Category
from app.schemas.transaction import (
    TransactionCreate, TransactionUpdate,
    TransactionFilters, MonthlySummary, CategoryAnalytics
)
from app.models.user import User
import uuid
import csv
import io
from datetime import datetime, timezone
from typing import List, Tuple
from app.services.categoriser_service import categoriser
from app.models.category import Category


class TransactionService:

    @staticmethod
    def create_transaction(
        db: Session,
        user: User,
        data: TransactionCreate
    ) -> Transaction:
        """Naya transaction — auto categorise karo."""

        # Auto categorise karo agar category manually nahi di
        category_id = data.category_id
        ml_confidence = 0.0

        if not category_id:
            text = f"{data.merchant_name or ''} {data.description}".strip()
            prediction = categoriser.predict(text)
            ml_confidence = prediction["confidence"]

            # DB mein us category ka naam dhundho
            category = db.query(Category).filter(
                Category.name == prediction["category"],
                Category.is_system == True
            ).first()

            if category:
                category_id = category.id

        transaction = Transaction(
            id=uuid.uuid4(),
            user_id=user.id,
            amount=data.amount,
            currency=data.currency,
            transaction_type=data.transaction_type,
            description=data.description,
            merchant_name=data.merchant_name,
            transaction_date=data.transaction_date,
            account_id=data.account_id,
            category_id=category_id,        # ← ML predicted category
            ml_category_confidence=ml_confidence,  # ← Confidence score
            is_manually_categorized=bool(data.category_id),
            notes=data.notes,
            status="completed"
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def get_transactions(
        db: Session,
        user: User,
        filters: TransactionFilters
    ) -> Tuple[List[Transaction], int]:
        """
        Filters ke saath transactions list karo.
        Tuple return karta hai: (transactions, total_count)
        Total count pagination ke liye chahiye.
        """
        query = db.query(Transaction).filter(
            Transaction.user_id == user.id
        )

        # Date range filter
        if filters.start_date:
            query = query.filter(
                Transaction.transaction_date >= filters.start_date
            )
        if filters.end_date:
            query = query.filter(
                Transaction.transaction_date <= filters.end_date
            )

        # Amount range filter
        if filters.min_amount is not None:
            query = query.filter(Transaction.amount >= filters.min_amount)
        if filters.max_amount is not None:
            query = query.filter(Transaction.amount <= filters.max_amount)

        # Transaction type filter
        if filters.transaction_type:
            query = query.filter(
                Transaction.transaction_type == filters.transaction_type
            )

        # Category filter
        if filters.category_id:
            query = query.filter(
                Transaction.category_id == filters.category_id
            )

        # Anomaly filter
        if filters.anomalies_only:
            query = query.filter(Transaction.is_anomaly == True)

        # Search — merchant_name YA description mein
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Transaction.merchant_name.ilike(search_term),
                    Transaction.description.ilike(search_term)
                )
            )

        # Total count (pagination ke liye — filter ke baad)
        total = query.count()

        # Sorting
        sort_col = getattr(Transaction, filters.sort_by,
                          Transaction.transaction_date)
        if filters.sort_order == "desc":
            query = query.order_by(desc(sort_col))
        else:
            query = query.order_by(asc(sort_col))

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        transactions = query.offset(offset).limit(filters.page_size).all()

        return transactions, total

    @staticmethod
    def get_transaction_by_id(
        db: Session,
        user: User,
        transaction_id: str
    ) -> Transaction:
        """Single transaction — sirf apni transactions dekh sakte ho."""
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user.id  # Security: dusre ka nahi dekh sakte
        ).first()

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        return transaction

    @staticmethod
    def update_transaction(
        db: Session,
        user: User,
        transaction_id: str,
        update_data: TransactionUpdate
    ) -> Transaction:
        """Transaction update karo."""
        transaction = TransactionService.get_transaction_by_id(
            db, user, transaction_id
        )

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(transaction, field, value)

        # Agar category manually set ki toh flag karo
        if 'category_id' in update_dict:
            transaction.is_manually_categorized = True

        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def delete_transaction(
        db: Session,
        user: User,
        transaction_id: str
    ) -> None:
        """Transaction delete karo."""
        transaction = TransactionService.get_transaction_by_id(
            db, user, transaction_id
        )
        db.delete(transaction)
        db.commit()

    @staticmethod
    def import_from_csv(
        db: Session,
        user: User,
        csv_content: str
    ) -> dict:
        """
        CSV file se bulk import karo.

        Expected CSV format:
        date,amount,type,description,merchant,category
        2025-01-15,500.00,debit,Zomato Order,Zomato,Dining Out
        2025-01-16,50000.00,credit,Salary,Company,Salary

        Real bank exports ka format alag hota hai —
        Day 9 mein bank-specific parsers banayenge.
        """
        imported = 0
        skipped = 0
        errors = []

        try:
            reader = csv.DictReader(io.StringIO(csv_content))
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CSV format: {str(e)}"
            )

        transactions_to_add = []

        for row_num, row in enumerate(reader, start=2):
            try:
                # Required fields validate karo
                if not row.get('amount') or not row.get('description'):
                    errors.append(f"Row {row_num}: Missing required fields")
                    skipped += 1
                    continue

                # Amount parse karo — commas remove karo (1,500.00 → 1500.00)
                amount_str = str(row['amount']).replace(',', '').strip()
                amount = float(amount_str)

                if amount <= 0:
                    errors.append(f"Row {row_num}: Invalid amount {amount}")
                    skipped += 1
                    continue

                # Transaction type determine karo
                type_str = row.get('type', 'debit').lower().strip()
                if type_str in ['debit', 'dr', 'expense', 'withdrawal']:
                    t_type = TransactionType.DEBIT
                elif type_str in ['credit', 'cr', 'income', 'deposit']:
                    t_type = TransactionType.CREDIT
                else:
                    t_type = TransactionType.DEBIT  # Default

                # Date parse karo — multiple formats handle karo
                date_str = row.get('date', '').strip()
                try:
                    # Common formats try karo
                    for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y',
                               '%m/%d/%Y', '%Y/%m/%d']:
                        try:
                            t_date = datetime.strptime(date_str, fmt)
                            t_date = t_date.replace(tzinfo=timezone.utc)
                            break
                        except ValueError:
                            continue
                    else:
                        t_date = datetime.now(timezone.utc)
                except Exception:
                    t_date = datetime.now(timezone.utc)

                transaction = Transaction(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    amount=amount,
                    currency=row.get('currency', 'INR').strip(),
                    transaction_type=t_type,
                    description=row['description'].strip(),
                    merchant_name=row.get('merchant', '').strip() or None,
                    transaction_date=t_date,
                    status="completed"
                )
                transactions_to_add.append(transaction)
                imported += 1

            except ValueError as e:
                errors.append(f"Row {row_num}: {str(e)}")
                skipped += 1
            except Exception as e:
                errors.append(f"Row {row_num}: Unexpected error — {str(e)}")
                skipped += 1

        # Bulk insert — ek ek se fast
        if transactions_to_add:
            db.bulk_save_objects(transactions_to_add)
            db.commit()

        return {
            "total_rows": imported + skipped,
            "imported": imported,
            "skipped": skipped,
            "errors": errors[:10]  # Max 10 errors show karo
        }

    @staticmethod
    def get_monthly_summary(
        db: Session,
        user: User,
        month: int,
        year: int
    ) -> MonthlySummary:
        """
        Kisi bhi month ka summary nikalo.
        Income, expenses, savings, top category.
        """
        from sqlalchemy import extract

        # Us month ki transactions
        base_query = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year
        )

        # Total income
        income_result = base_query.filter(
            Transaction.transaction_type == TransactionType.CREDIT
        ).with_entities(func.sum(Transaction.amount)).scalar()
        total_income = float(income_result or 0)

        # Total expenses
        expense_result = base_query.filter(
            Transaction.transaction_type == TransactionType.DEBIT
        ).with_entities(func.sum(Transaction.amount)).scalar()
        total_expenses = float(expense_result or 0)

        # Transaction count
        count = base_query.count()

        # Top category dhundho
        top_cat_result = db.query(
            Category.name,
            func.sum(Transaction.amount).label('total')
        ).join(
            Transaction,
            Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_type == TransactionType.DEBIT,
            extract('month', Transaction.transaction_date) == month,
            extract('year', Transaction.transaction_date) == year
        ).group_by(Category.name).order_by(desc('total')).first()

        top_category = top_cat_result[0] if top_cat_result else None

        return MonthlySummary(
            month=month,
            year=year,
            total_income=round(total_income, 2),
            total_expenses=round(total_expenses, 2),
            net_savings=round(total_income - total_expenses, 2),
            transaction_count=count,
            top_category=top_category
        )

    @staticmethod
    def get_category_analytics(
        db: Session,
        user: User,
        month: int = None,
        year: int = None
    ) -> List[CategoryAnalytics]:
        """
        Category-wise spending breakdown.
        Dashboard pie chart ke liye data.
        """
        from sqlalchemy import extract

        query = db.query(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            func.sum(Transaction.amount).label('total_amount'),
            func.count(Transaction.id).label('transaction_count'),
            func.avg(Transaction.amount).label('avg_transaction')
        ).outerjoin(
            Transaction,
            Transaction.category_id == Category.id
        ).filter(
            Transaction.user_id == user.id,
            Transaction.transaction_type == TransactionType.DEBIT
        )

        if month:
            query = query.filter(
                extract('month', Transaction.transaction_date) == month
            )
        if year:
            query = query.filter(
                extract('year', Transaction.transaction_date) == year
            )

        results = query.group_by(
            Category.id, Category.name
        ).order_by(desc('total_amount')).all()

        # Total calculate karo percentage ke liye
        grand_total = sum(r.total_amount or 0 for r in results)

        analytics = []
        for r in results:
            if r.total_amount and r.total_amount > 0:
                analytics.append(CategoryAnalytics(
                    category_id=r.category_id,
                    category_name=r.category_name,
                    total_amount=round(float(r.total_amount), 2),
                    transaction_count=r.transaction_count,
                    percentage=round(
                        (float(r.total_amount) / grand_total * 100)
                        if grand_total > 0 else 0, 1
                    ),
                    avg_transaction=round(float(r.avg_transaction or 0), 2)
                ))

        return analytics