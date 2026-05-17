from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import UserRole
from app.models.city import Alert, CityZone
from app.schemas.alerts import AlertResponse, AlertCreate

router = APIRouter()


def _enrich(alert: Alert, db: Session) -> AlertResponse:
    zone_name = None
    if alert.zone_id:
        z = db.query(CityZone).filter(CityZone.id == alert.zone_id).first()
        zone_name = z.name if z else None
    return AlertResponse(
        id=alert.id,
        zone_id=alert.zone_id,
        zone_name=zone_name,
        alert_type=alert.alert_type,
        priority=alert.priority,
        title=alert.title,
        message=alert.message,
        is_resolved=alert.is_resolved,
        created_at=alert.created_at,
    )


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    resolved: bool | None = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    q = db.query(Alert).order_by(Alert.created_at.desc())
    if resolved is not None:
        q = q.filter(Alert.is_resolved == resolved)
    return [_enrich(a, db) for a in q.limit(limit).all()]


@router.post("", response_model=AlertResponse)
def create_alert(
    data: AlertCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.ADMIN, UserRole.CITY_OPERATOR)),
):
    alert = Alert(**data.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return _enrich(alert, db)


@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.acknowledged_by = user.id
    db.commit()
    db.refresh(alert)
    return _enrich(alert, db)
