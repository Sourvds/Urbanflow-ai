from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.services.analytics import AnalyticsService

router = APIRouter()


@router.get("/analytics")
def water_analytics(
    zone_id: int | None = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return AnalyticsService(db).water_analytics(zone_id)
