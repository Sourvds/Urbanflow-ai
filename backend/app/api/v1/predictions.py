from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import UserRole
from app.models.city import AIPrediction, CityZone
from app.schemas.predictions import PredictionResponse
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("", response_model=list[PredictionResponse])
def list_predictions(
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    preds = db.query(AIPrediction).order_by(AIPrediction.created_at.desc()).limit(limit).all()
    zone_map = {z.id: z.name for z in db.query(CityZone).all()}
    return [
        PredictionResponse(
            id=p.id,
            zone_id=p.zone_id,
            zone_name=zone_map.get(p.zone_id),
            prediction_type=p.prediction_type.value,
            predicted_value=p.predicted_value,
            confidence_score=p.confidence_score,
            horizon_hours=p.horizon_hours,
            model_name=p.model_name,
            created_at=p.created_at,
        )
        for p in preds
    ]


@router.post("/run")
def run_predictions(
    db: Session = Depends(get_db),
    _user=Depends(require_roles(UserRole.ADMIN, UserRole.CITY_OPERATOR)),
):
    results = AnalyticsService(db).run_predictions()
    return {"status": "ok", "predictions": results}
