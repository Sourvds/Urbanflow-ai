from datetime import datetime
from pydantic import BaseModel


class PredictionResponse(BaseModel):
    id: int
    zone_id: int | None
    zone_name: str | None = None
    prediction_type: str
    predicted_value: float
    confidence_score: float
    horizon_hours: int
    model_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class OptimizationResponse(BaseModel):
    id: int
    zone_id: int | None
    zone_name: str | None = None
    resource_type: str
    recommendation: str
    expected_savings_percent: float
    priority: str
    applied: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ForecastPoint(BaseModel):
    timestamp: str
    actual: float | None
    predicted: float
    lower_bound: float | None = None
    upper_bound: float | None = None


class ModuleAnalytics(BaseModel):
    summary: dict
    hourly_series: list[dict]
    district_breakdown: list[dict]
    forecasts: list[ForecastPoint]
    anomalies: list[dict]
    recommendations: list[str]
