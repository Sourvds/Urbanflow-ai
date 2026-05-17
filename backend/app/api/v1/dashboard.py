from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.services.analytics import AnalyticsService
from app.schemas.dashboard import DashboardOverview

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
def dashboard_overview(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return AnalyticsService(db).get_dashboard_overview()
