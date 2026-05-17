from datetime import datetime
from sqlalchemy import (
    String, Float, Integer, DateTime, ForeignKey, Text, Boolean, Index, Enum as SAEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class AlertPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, enum.Enum):
    ELECTRICITY = "electricity"
    TRAFFIC = "traffic"
    WATER = "water"
    POLLUTION = "pollution"
    SENSOR = "sensor"
    SYSTEM = "system"


class PredictionType(str, enum.Enum):
    ELECTRICITY = "electricity"
    TRAFFIC = "traffic"
    WATER = "water"
    ENVIRONMENT = "environment"


class CityZone(Base):
    __tablename__ = "city_zones"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    sector_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    population: Mapped[int] = mapped_column(Integer, default=0)
    area_km2: Mapped[float] = mapped_column(Float, default=1.0)
    efficiency_score: Mapped[float] = mapped_column(Float, default=75.0, index=True)
    carbon_estimate_tons: Mapped[float] = mapped_column(Float, default=0.0)

    electricity_records = relationship("ElectricityUsage", back_populates="zone")
    water_records = relationship("WaterUsage", back_populates="zone")
    traffic_records = relationship("TrafficData", back_populates="zone")
    environmental_records = relationship("EnvironmentalData", back_populates="zone")
    sensors = relationship("SensorData", back_populates="zone")


class ElectricityUsage(Base):
    __tablename__ = "electricity_usage"
    __table_args__ = (Index("ix_electricity_zone_timestamp", "zone_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("city_zones.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    consumption_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    peak_demand_kw: Mapped[float] = mapped_column(Float, default=0.0)
    renewable_ratio: Mapped[float] = mapped_column(Float, default=0.3)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    zone = relationship("CityZone", back_populates="electricity_records")


class WaterUsage(Base):
    __tablename__ = "water_usage"
    __table_args__ = (Index("ix_water_zone_timestamp", "zone_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("city_zones.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    consumption_liters: Mapped[float] = mapped_column(Float, nullable=False)
    pressure_psi: Mapped[float] = mapped_column(Float, default=45.0)
    leak_probability: Mapped[float] = mapped_column(Float, default=0.0)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    zone = relationship("CityZone", back_populates="water_records")


class TrafficData(Base):
    __tablename__ = "traffic_data"
    __table_args__ = (Index("ix_traffic_zone_timestamp", "zone_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("city_zones.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    congestion_level: Mapped[float] = mapped_column(Float, nullable=False)
    avg_speed_kmh: Mapped[float] = mapped_column(Float, default=40.0)
    vehicle_count: Mapped[int] = mapped_column(Integer, default=0)
    signal_wait_seconds: Mapped[float] = mapped_column(Float, default=60.0)
    accident_risk_score: Mapped[float] = mapped_column(Float, default=0.1)

    zone = relationship("CityZone", back_populates="traffic_records")


class EnvironmentalData(Base):
    __tablename__ = "environmental_data"
    __table_args__ = (Index("ix_env_zone_timestamp", "zone_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("city_zones.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    aqi: Mapped[float] = mapped_column(Float, nullable=False)
    pm25: Mapped[float] = mapped_column(Float, default=25.0)
    temperature_c: Mapped[float] = mapped_column(Float, default=22.0)
    humidity_percent: Mapped[float] = mapped_column(Float, default=50.0)
    noise_db: Mapped[float] = mapped_column(Float, default=55.0)

    zone = relationship("CityZone", back_populates="environmental_records")


class SensorData(Base):
    __tablename__ = "sensor_data"
    __table_args__ = (Index("ix_sensor_zone_type", "zone_id", "sensor_type"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("city_zones.id"), nullable=False, index=True)
    sensor_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="")
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)

    zone = relationship("CityZone", back_populates="sensors")


class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    __table_args__ = (Index("ix_prediction_type_created", "prediction_type", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("city_zones.id"), nullable=True, index=True)
    prediction_type: Mapped[PredictionType] = mapped_column(
        SAEnum(PredictionType, name="prediction_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    predicted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    horizon_hours: Mapped[int] = mapped_column(Integer, default=24)
    model_name: Mapped[str] = mapped_column(String(100), default="xgboost")
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class OptimizationLog(Base):
    __tablename__ = "optimization_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("city_zones.id"), nullable=True, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    expected_savings_percent: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[str] = mapped_column(String(20), default="medium")
    applied: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("ix_alert_priority_resolved", "priority", "is_resolved"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    zone_id: Mapped[int | None] = mapped_column(ForeignKey("city_zones.id"), nullable=True, index=True)
    alert_type: Mapped[AlertType] = mapped_column(
        SAEnum(AlertType, name="alert_type", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )
    priority: Mapped[AlertPriority] = mapped_column(
        SAEnum(AlertPriority, name="alert_priority", values_callable=lambda x: [e.value for e in x]),
        default=AlertPriority.MEDIUM,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    acknowledged_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    acknowledged_by_user = relationship("User", back_populates="alerts", foreign_keys=[acknowledged_by])


class SystemLog(Base):
    __tablename__ = "system_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    level: Mapped[str] = mapped_column(String(20), default="info", index=True)
    component: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
