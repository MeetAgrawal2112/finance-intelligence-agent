# app/tasks/anomaly_scan.py
"""
Daily anomaly scan task.
Sab users ki recent transactions check karo.
"""

from app.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(
    name="app.tasks.anomaly_scan.scan_all_users",
    bind=True,
)
def scan_all_users(self):
    """
    Roz subah 9 baje:
    1. Sab active users ke liye
    2. Last 24 hours ki transactions check karo
    3. Anomalies pe alerts create karo
    """
    try:
        from app.db.session import SessionLocal
        from app.models.user import User
        from app.models.transaction import Transaction, TransactionType
        from app.models.alert import Alert, AlertType, AlertSeverity
        from app.models.category import Category
        from app.services.anomaly_service import anomaly_detector
        from datetime import datetime, timedelta, timezone
        import uuid

        db = SessionLocal()
        total_scanned = 0
        total_anomalies = 0

        try:
            users = db.query(User).filter(User.is_active == True).all()
            since = datetime.now(timezone.utc) - timedelta(hours=24)

            for user in users:
                recent_txns = db.query(Transaction).filter(
                    Transaction.user_id == user.id,
                    Transaction.transaction_date >= since,
                    Transaction.transaction_type == TransactionType.DEBIT
                ).all()

                for txn in recent_txns:
                    total_scanned += 1

                    cat_name = "Other"
                    if txn.category_id:
                        cat = db.query(Category).filter(
                            Category.id == txn.category_id
                        ).first()
                        if cat:
                            cat_name = cat.name

                    result = anomaly_detector.analyze_transaction(
                        amount=txn.amount,
                        description=txn.description,
                        transaction_date=txn.transaction_date,
                        user_id=str(user.id),
                        category=cat_name
                    )

                    if result["is_anomaly"] and not txn.is_anomaly:
                        txn.is_anomaly = True
                        txn.anomaly_score = result["anomaly_score"]

                        # Alert create karo
                        severity_map = {
                            "high": AlertSeverity.HIGH,
                            "medium": AlertSeverity.MEDIUM,
                            "low": AlertSeverity.LOW,
                        }

                        alert = Alert(
                            id=uuid.uuid4(),
                            user_id=user.id,
                            transaction_id=txn.id,
                            alert_type=AlertType.ANOMALY,
                            severity=severity_map[result["severity"]],
                            title=f"Suspicious: ₹{txn.amount:,.0f} - {txn.merchant_name or txn.description[:30]}",
                            message=(
                                f"Unusual transaction detected.\n"
                                f"Reasons: {', '.join(result['reasons'])}\n"
                                f"Score: {result['anomaly_score']:.0%}"
                            ),
                        )
                        db.add(alert)
                        total_anomalies += 1

            db.commit()

            result = {
                "status": "success",
                "users_scanned": len(users),
                "transactions_scanned": total_scanned,
                "anomalies_found": total_anomalies,
            }
            logger.info(f"Anomaly scan complete: {result}")
            return result

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Anomaly scan failed: {e}")
        raise self.retry(exc=e, countdown=300)