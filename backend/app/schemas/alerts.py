from datetime import datetime
from pydantic import BaseModel
from app.models.city import AlertType, AlertPriority


class AlertCreate(BaseModel):
    zone_id: int | None = None
    alert_type: AlertType
    priority: AlertPriority = AlertPriority.MEDIUM
    title: str
    message: str


class AlertResponse(BaseModel):
    id: int
    zone_id: int | None
    zone_name: str | None = None
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True
