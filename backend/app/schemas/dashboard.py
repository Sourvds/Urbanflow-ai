from datetime import datetime
from pydantic import BaseModel


class MetricCard(BaseModel):
    label: str
    value: float
    unit: str
    change_percent: float
    trend: str


class RecommendationItem(BaseModel):
    id: int
    resource_type: str
    recommendation: str
    expected_savings_percent: float
    priority: str
    zone_name: str | None = None


class ActivityItem(BaseModel):
    id: int
    message: str
    component: str
    level: str
    created_at: datetime


class DashboardOverview(BaseModel):
    electricity_kwh: float
    traffic_congestion: float
    water_liters: float
    air_quality_index: float
    energy_efficiency_score: float
    city_efficiency_score: float
    active_alerts: int
    carbon_emission_tons: float
    metrics: list[MetricCard]
    recommendations: list[RecommendationItem]
    recent_activity: list[ActivityItem]
    district_rankings: list[dict]


class ZoneMapPoint(BaseModel):
    id: int
    name: str
    sector_code: str
    latitude: float
    longitude: float
    electricity_kwh: float
    water_liters: float
    congestion: float
    aqi: float
    efficiency_score: float
    alert_count: int
