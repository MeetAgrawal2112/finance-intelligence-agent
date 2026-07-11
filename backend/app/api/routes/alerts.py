# app/api/routes/alerts.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.alert import Alert, AlertType, AlertSeverity
from app.schemas.common import SuccessResponse
from typing import Optional
import uuid
from datetime import datetime, timezone

router = APIRouter()

@router.get("")
def get_alerts(
    is_read: Optional[bool] = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sab alerts list karo."""
    query = db.query(Alert).filter(
        Alert.user_id == current_user.id
    )
    if is_read is not None:
        query = query.filter(Alert.is_read == is_read)

    alerts = query.order_by(
        Alert.created_at.desc()
    ).limit(limit).all()

    total_unread = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_read == False
    ).count()

    return SuccessResponse(
        data={
            "alerts": [
                {
                    "id": str(a.id),
                    "alert_type": a.alert_type.value,
                    "severity": a.severity.value,
                    "title": a.title,
                    "message": a.message,
                    "is_read": a.is_read,
                    "is_resolved": a.is_resolved,
                    "transaction_id": str(a.transaction_id) if a.transaction_id else None,
                    "created_at": a.created_at.isoformat(),
                }
                for a in alerts
            ],
            "total_unread": total_unread,
        }
    )

@router.put("/{alert_id}/read")
def mark_read(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alert read mark karo."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()

    if alert:
        alert.is_read = True
        db.commit()

    return SuccessResponse(message="Marked as read")

@router.put("/{alert_id}/resolve")
def mark_resolved(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alert resolve karo."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == current_user.id
    ).first()

    if alert:
        alert.is_read = True
        alert.is_resolved = True
        db.commit()

    return SuccessResponse(message="Alert resolved")

@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sab alerts read mark karo."""
    db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_read == False
    ).update({"is_read": True})
    db.commit()

    return SuccessResponse(message="All alerts marked as read")

@router.post("/test")
def create_test_alert(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Test alert create karo — development ke liye."""
    alert = Alert(
        id=uuid.uuid4(),
        user_id=current_user.id,
        alert_type=AlertType.ANOMALY,
        severity=AlertSeverity.HIGH,
        title="Test: Unusual transaction ₹95,000",
        message="Yeh ek test alert hai. Ek bahut badi transaction detect hui hai.",
        is_read=False,
        is_resolved=False,
    )
    db.add(alert)
    db.commit()
    return SuccessResponse(message="Test alert created!")