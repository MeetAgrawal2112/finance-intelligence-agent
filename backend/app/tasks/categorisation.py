# app/tasks/categorisation.py
"""
Nightly re-categorisation task.
Sab uncategorised transactions ko ML model se categorise karo.
"""

from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(
    name="app.tasks.categorisation.recategorise_all_transactions",
    bind=True,
    max_retries=3,
)
def recategorise_all_transactions(self):
    """
    Raat 2 baje:
    1. Sab uncategorised transactions dhundho
    2. ML model se category predict karo
    3. Low confidence transactions flag karo
    """
    try:
        from app.db.session import SessionLocal
        from app.models.transaction import Transaction, TransactionType
        from app.models.category import Category
        from app.services.categoriser_service import categoriser

        db = SessionLocal()
        updated = 0
        errors = 0

        try:
            # Uncategorised debit transactions
            uncategorised = db.query(Transaction).filter(
                Transaction.category_id == None,
                Transaction.transaction_type == TransactionType.DEBIT,
                Transaction.is_manually_categorized == False
            ).limit(1000).all()

            logger.info(f"Found {len(uncategorised)} uncategorised transactions")

            for txn in uncategorised:
                try:
                    text = f"{txn.merchant_name or ''} {txn.description}".strip()
                    prediction = categoriser.predict(text)

                    category = db.query(Category).filter(
                        Category.name == prediction["category"],
                        Category.is_system == True
                    ).first()

                    if category:
                        txn.category_id = category.id
                        txn.ml_category_confidence = prediction["confidence"]
                        updated += 1

                except Exception as e:
                    errors += 1
                    logger.error(f"Error categorising txn {txn.id}: {e}")

            db.commit()

            result = {
                "status": "success",
                "updated": updated,
                "errors": errors,
                "total": len(uncategorised)
            }
            logger.info(f"Categorisation complete: {result}")
            return result

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Categorisation task failed: {e}")
        raise self.retry(exc=e, countdown=300)