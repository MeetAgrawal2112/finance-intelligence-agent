# app/services/langchain/tools.py
"""
LangChain Tools — Agent ke paas yeh weapons hain!
Har tool ek specific kaam karta hai.
Agent decide karta hai kaunsa tool use karna hai.
"""

from langchain.tools import tool
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

# ─── Tool 1: Monthly Summary ──────────────────────────────────────────────────

def make_monthly_summary_tool(db: Session, user_id: str):
    @tool
    def get_monthly_summary(month: int, year: int) -> str:
        """
        Kisi bhi month ka financial summary nikalo.
        Income, expenses, savings, top category sab milega.
        Use when user asks about monthly spending, budget, savings.

        Args:
            month: Month number (1-12)
            year: Year (e.g. 2025, 2026)
        """
        try:
            from app.models.transaction import Transaction, TransactionType
            from app.models.category import Category
            from sqlalchemy import func, extract

            # Income
            income = db.query(
                func.sum(Transaction.amount)
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.CREDIT,
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            ).scalar() or 0

            # Expenses
            expenses = db.query(
                func.sum(Transaction.amount)
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEBIT,
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            ).scalar() or 0

            # Transaction count
            count = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            ).count()

            # Top category
            top_cat = db.query(
                Category.name,
                func.sum(Transaction.amount).label('total')
            ).join(
                Transaction,
                Transaction.category_id == Category.id
            ).filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEBIT,
                extract('month', Transaction.transaction_date) == month,
                extract('year', Transaction.transaction_date) == year
            ).group_by(Category.name).order_by(
                func.sum(Transaction.amount).desc()
            ).first()

            savings = float(income) - float(expenses)
            savings_rate = (savings / float(income) * 100) if income > 0 else 0

            result = f"""
Month: {month}/{year}
Total Income: Rs.{float(income):,.0f}
Total Expenses: Rs.{float(expenses):,.0f}
Net Savings: Rs.{savings:,.0f}
Savings Rate: {savings_rate:.1f}%
Transaction Count: {count}
Top Spending Category: {top_cat[0] if top_cat else 'N/A'} (Rs.{float(top_cat[1]):,.0f} if top_cat else '')
"""
            return result.strip()

        except Exception as e:
            return f"Error getting monthly summary: {str(e)}"

    return get_monthly_summary


# ─── Tool 2: Category Spending ────────────────────────────────────────────────

def make_category_spending_tool(db: Session, user_id: str):
    @tool
    def get_category_spending(
        category_name: str,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> str:
        """
        Specific category ka spending details nikalo.
        Use when user asks about specific category like
        groceries, dining, transport, etc.

        Args:
            category_name: Category name (e.g. 'Groceries', 'Dining Out')
            month: Optional month filter (1-12)
            year: Optional year filter
        """
        try:
            from app.models.transaction import Transaction, TransactionType
            from app.models.category import Category
            from sqlalchemy import func, extract

            query = db.query(
                func.sum(Transaction.amount).label('total'),
                func.count(Transaction.id).label('count'),
                func.avg(Transaction.amount).label('avg'),
                func.max(Transaction.amount).label('max_amt'),
            ).join(
                Category,
                Transaction.category_id == Category.id
            ).filter(
                Transaction.user_id == user_id,
                Category.name.ilike(f"%{category_name}%"),
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

            result = query.first()

            if not result or not result.total:
                return f"No transactions found for category '{category_name}'"

            # Top merchants in this category
            merchants = db.query(
                Transaction.merchant_name,
                func.sum(Transaction.amount).label('total')
            ).join(
                Category,
                Transaction.category_id == Category.id
            ).filter(
                Transaction.user_id == user_id,
                Category.name.ilike(f"%{category_name}%"),
                Transaction.merchant_name.isnot(None)
            ).group_by(
                Transaction.merchant_name
            ).order_by(
                func.sum(Transaction.amount).desc()
            ).limit(3).all()

            merchant_str = ", ".join(
                [f"{m[0]} (Rs.{float(m[1]):,.0f})" for m in merchants]
            ) if merchants else "N/A"

            period = f"{month}/{year}" if month and year else "All time"

            return f"""
Category: {category_name}
Period: {period}
Total Spent: Rs.{float(result.total):,.0f}
Transactions: {result.count}
Average per transaction: Rs.{float(result.avg):,.0f}
Largest transaction: Rs.{float(result.max_amt):,.0f}
Top merchants: {merchant_str}
""".strip()

        except Exception as e:
            return f"Error: {str(e)}"

    return get_category_spending


# ─── Tool 3: Recent Transactions ──────────────────────────────────────────────

def make_recent_transactions_tool(db: Session, user_id: str):
    @tool
    def get_recent_transactions(limit: int = 10) -> str:
        """
        Recent transactions list karo.
        Use when user asks about latest transactions,
        recent spending, or wants to see transaction history.

        Args:
            limit: Number of transactions to return (max 20)
        """
        try:
            from app.models.transaction import Transaction
            from app.models.category import Category

            limit = min(limit, 20)

            txns = db.query(Transaction).filter(
                Transaction.user_id == user_id
            ).order_by(
                Transaction.transaction_date.desc()
            ).limit(limit).all()

            if not txns:
                return "No transactions found"

            lines = [f"Last {len(txns)} transactions:"]
            for t in txns:
                date = t.transaction_date.strftime("%d %b")
                type_icon = "💸" if t.transaction_type.value == "debit" else "💰"
                merchant = t.merchant_name or t.description[:30]
                lines.append(
                    f"{type_icon} {date} | {merchant} | "
                    f"Rs.{t.amount:,.0f} | "
                    f"{'ANOMALY 🚨' if t.is_anomaly else 'Normal'}"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error: {str(e)}"

    return get_recent_transactions


# ─── Tool 4: Spending Forecast ────────────────────────────────────────────────

def make_forecast_tool():
    @tool
    def get_spending_forecast() -> str:
        """
        Next 30 days ka spending forecast nikalo.
        Use when user asks about future spending,
        budget planning, or savings potential.
        """
        try:
            from app.services.prediction_service import predictor

            if not predictor.is_loaded:
                return "Forecast model not available"

            forecast = predictor.predict_next_month()
            predictions = forecast.get("predictions", [])
            total = forecast.get("total_predicted", 0)
            savings = forecast.get("savings_potential", 0)

            lines = [
                f"Next 30 days spending forecast:",
                f"Period: {forecast['forecast_period']['start']} to "
                f"{forecast['forecast_period']['end']}",
                ""
            ]

            for p in predictions[:5]:
                trend = "↑" if p['trend'] == 'increasing' else \
                        "↓" if p['trend'] == 'decreasing' else "→"
                lines.append(
                    f"{trend} {p['category']:<20} "
                    f"Rs.{p['predicted_amount']:>8,.0f}"
                )

            lines.extend([
                f"",
                f"Total Predicted: Rs.{total:,.0f}",
                f"Savings Potential: Rs.{savings:,.0f} "
                f"(if top categories cut by 20%)"
            ])

            return "\n".join(lines)

        except Exception as e:
            return f"Error: {str(e)}"

    return get_spending_forecast


# ─── Tool 5: Anomaly Check ────────────────────────────────────────────────────

def make_anomaly_tool(db: Session, user_id: str):
    @tool
    def get_anomalies(limit: int = 5) -> str:
        """
        Unusual ya suspicious transactions nikalo.
        Use when user asks about suspicious activity,
        anomalies, unusual spending, or fraud alerts.

        Args:
            limit: Number of anomalies to return
        """
        try:
            from app.models.transaction import Transaction
            from app.models.alert import Alert

            anomalies = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.is_anomaly == True
            ).order_by(
                Transaction.anomaly_score.desc()
            ).limit(limit).all()

            if not anomalies:
                return "Koi suspicious transaction nahi mili! Sab normal lag raha hai. ✅"

            lines = [f"Found {len(anomalies)} suspicious transactions:"]
            for t in anomalies:
                date = t.transaction_date.strftime("%d %b %Y")
                severity = "🔴 HIGH" if t.anomaly_score > 0.75 else \
                          "🟡 MEDIUM" if t.anomaly_score > 0.5 else "🟢 LOW"
                lines.append(
                    f"{severity} | {date} | "
                    f"{t.merchant_name or t.description[:25]} | "
                    f"Rs.{t.amount:,.0f} | "
                    f"Score: {t.anomaly_score:.0%}"
                )

            return "\n".join(lines)

        except Exception as e:
            return f"Error: {str(e)}"

    return get_anomalies


# ─── Tool 6: Savings Advice ───────────────────────────────────────────────────

def make_savings_tool():
    @tool
    def get_savings_advice(monthly_income: float = 50000) -> str:
        """
        Personalized savings advice aur budget recommendations.
        Use when user asks how much they can save,
        budget advice, or financial planning tips.

        Args:
            monthly_income: User's monthly income in INR
        """
        try:
            from app.services.prediction_service import predictor

            forecast = predictor.predict_next_month()
            total_expenses = forecast.get("total_predicted", 0)
            advice = predictor.get_savings_advice(total_expenses, monthly_income)

            needs = monthly_income * 0.50
            wants = monthly_income * 0.30
            savings_target = monthly_income * 0.20

            return f"""
Savings Analysis (Monthly Income: Rs.{monthly_income:,.0f}):

Predicted Expenses: Rs.{total_expenses:,.0f}
Predicted Savings: Rs.{advice['predicted_savings']:,.0f}
Savings Rate: {advice['savings_rate']:.1f}%
Status: {advice['status'].upper()}

50-30-20 Budget Rule:
  Needs (50%):   Rs.{needs:,.0f}
  Wants (30%):   Rs.{wants:,.0f}
  Savings (20%): Rs.{savings_target:,.0f}

Advice: {advice['message']}
""".strip()

        except Exception as e:
            return f"Error: {str(e)}"

    return get_savings_advice