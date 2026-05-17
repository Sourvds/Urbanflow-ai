from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import UserRole
from app.models.city import OptimizationLog, CityZone
from app.schemas.predictions import OptimizationResponse
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/recommendations", response_model=list[OptimizationResponse])
def get_recommendations(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    logs = (
        db.query(OptimizationLog)
        .order_by(OptimizationLog.created_at.desc())
        .limit(limit)
        .all()
    )
    zone_map = {z.id: z.name for z in db.query(CityZone).all()}
    return [
        OptimizationResponse(
            id=l.id,
            zone_id=l.zone_id,
            zone_name=zone_map.get(l.zone_id),
            resource_type=l.resource_type,
            recommendation=l.recommendation,
            expected_savings_percent=l.expected_savings_percent,
            priority=l.priority,
            applied=l.applied,
            created_at=l.created_at,
        )
        for l in logs
    ]


@router.post("/generate")
def generate_optimizations(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.ADMIN, UserRole.CITY_OPERATOR)),
):
    count = AnalyticsService(db).generate_optimizations()
    return {"status": "ok", "generated": count}
