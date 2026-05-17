from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.models.city import (
    Alert, AIPrediction, OptimizationLog, SensorData, SystemLog, CityZone
)
from app.schemas.auth import UserResponse
from app.services.analytics import AnalyticsService

router = APIRouter(dependencies=[Depends(require_roles(UserRole.ADMIN))])


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return [UserResponse.model_validate(u) for u in db.query(User).all()]


@router.get("/stats")
def admin_stats(db: Session = Depends(get_db)):
    return {
        "users": db.query(func.count(User.id)).scalar(),
        "zones": db.query(func.count(CityZone.id)).scalar(),
        "active_alerts": db.query(func.count(Alert.id)).filter(Alert.is_resolved == False).scalar(),
        "predictions": db.query(func.count(AIPrediction.id)).scalar(),
        "optimizations": db.query(func.count(OptimizationLog.id)).scalar(),
        "sensors": db.query(func.count(SensorData.id)).scalar(),
        "system_logs": db.query(func.count(SystemLog.id)).scalar(),
    }


@router.get("/sql-reports")
def sql_reports(db: Session = Depends(get_db)):
    return AnalyticsService(db).sql_analytics_report()


@router.get("/system-health")
def system_health(db: Session = Depends(get_db)):
    active_sensors = (
        db.query(func.count(SensorData.id))
        .filter(SensorData.status == "active")
        .scalar()
    )
    failed_sensors = (
        db.query(func.count(SensorData.id))
        .filter(SensorData.status == "failed")
        .scalar()
    )
    recent_errors = (
        db.query(SystemLog)
        .filter(SystemLog.level == "error")
        .order_by(SystemLog.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "status": "healthy" if failed_sensors < 5 else "degraded",
        "active_sensors": active_sensors,
        "failed_sensors": failed_sensors,
        "uptime_percent": 99.7,
        "recent_errors": [
            {"component": e.component, "message": e.message, "created_at": e.created_at}
            for e in recent_errors
        ],
    }
