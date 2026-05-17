"""Generate realistic smart city demo data for UrbanFlow AI."""
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.city import (
    CityZone,
    ElectricityUsage,
    WaterUsage,
    TrafficData,
    EnvironmentalData,
    SensorData,
    AIPrediction,
    OptimizationLog,
    Alert,
    SystemLog,
    AlertType,
    AlertPriority,
    PredictionType,
)
from app.core.security import get_password_hash
from app.ml.forecasting import ForecastEngine
from app.ml.optimization import OptimizationEngine

ZONES = [
    ("Central District", "CD-01", 40.7128, -74.0060, 85000, 4.2),
    ("North Harbor", "NH-02", 40.7282, -73.9942, 62000, 3.8),
    ("East Innovation", "EI-03", 40.7061, -73.9857, 45000, 2.9),
    ("South Industrial", "SI-04", 40.6892, -74.0445, 38000, 5.1),
    ("West Residential", "WR-05", 40.7359, -74.0301, 92000, 6.4),
    ("Park District", "PD-06", 40.7505, -73.9934, 55000, 3.2),
    ("Tech Corridor", "TC-07", 40.7614, -73.9776, 71000, 2.5),
    ("Riverside", "RV-08", 40.7023, -74.0158, 48000, 4.0),
    ("Airport Zone", "AZ-09", 40.6413, -73.7781, 25000, 8.2),
    ("University Quarter", "UQ-10", 40.8075, -73.9626, 67000, 3.6),
]

DEMO_USERS = [
    ("admin@urbanflow.ai", "Admin User", UserRole.ADMIN, "UrbanFlow2026!"),
    ("operator@urbanflow.ai", "City Operator", UserRole.CITY_OPERATOR, "UrbanFlow2026!"),
    ("analyst@urbanflow.ai", "Data Analyst", UserRole.ANALYST, "UrbanFlow2026!"),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding users...")
        for email, name, role, pwd in DEMO_USERS:
            db.add(User(
                email=email,
                full_name=name,
                role=role,
                hashed_password=get_password_hash(pwd),
            ))
        db.commit()

        print("Seeding city zones...")
        zones = []
        for name, code, lat, lon, pop, area in ZONES:
            z = CityZone(
                name=name,
                sector_code=code,
                latitude=lat,
                longitude=lon,
                population=pop,
                area_km2=area,
                efficiency_score=round(random.uniform(68, 95), 1),
                carbon_estimate_tons=round(random.uniform(120, 450), 1),
            )
            db.add(z)
            zones.append(z)
        db.commit()
        for z in zones:
            db.refresh(z)

        print("Generating time-series data (7 days hourly)...")
        now = datetime.utcnow()
        forecast = ForecastEngine()
        optimizer = OptimizationEngine()

        for z in zones:
            base_elec = random.uniform(800, 2500)
            base_water = random.uniform(50000, 150000)
            base_cong = random.uniform(0.25, 0.65)

            for hours_ago in range(168, 0, -1):
                ts = now - timedelta(hours=hours_ago)
                hour = ts.hour
                day_factor = 1.0 + 0.3 * (1 if 8 <= hour <= 20 else -0.2)
                weekend_factor = 0.85 if ts.weekday() >= 5 else 1.0
                noise = random.uniform(0.92, 1.08)

                elec = base_elec * day_factor * weekend_factor * noise
                is_elec_anomaly = random.random() < 0.02
                if is_elec_anomaly:
                    elec *= random.uniform(1.4, 1.8)

                db.add(ElectricityUsage(
                    zone_id=z.id,
                    timestamp=ts,
                    consumption_kwh=round(elec, 2),
                    peak_demand_kw=round(elec * 0.15, 2),
                    renewable_ratio=round(random.uniform(0.2, 0.55), 2),
                    is_anomaly=is_elec_anomaly,
                ))

                water = base_water * day_factor * weekend_factor * noise
                leak_prob = random.uniform(0, 0.15)
                if random.random() < 0.01:
                    leak_prob = random.uniform(0.65, 0.92)
                is_water_anomaly = leak_prob > 0.7 or random.random() < 0.015

                db.add(WaterUsage(
                    zone_id=z.id,
                    timestamp=ts,
                    consumption_liters=round(water, 0),
                    pressure_psi=round(random.uniform(38, 52), 1),
                    leak_probability=round(leak_prob, 3),
                    is_anomaly=is_water_anomaly,
                ))

                cong = min(0.98, base_cong * day_factor * noise * (1.2 if 7 <= hour <= 9 or 17 <= hour <= 19 else 1.0))
                db.add(TrafficData(
                    zone_id=z.id,
                    timestamp=ts,
                    congestion_level=round(cong, 3),
                    avg_speed_kmh=round(60 * (1 - cong * 0.7), 1),
                    vehicle_count=int(random.uniform(200, 1200) * cong),
                    signal_wait_seconds=round(45 + cong * 80, 1),
                    accident_risk_score=round(cong * random.uniform(0.1, 0.4), 3),
                ))

                db.add(EnvironmentalData(
                    zone_id=z.id,
                    timestamp=ts,
                    aqi=round(random.uniform(35, 120) + cong * 20, 1),
                    pm25=round(random.uniform(8, 45), 1),
                    temperature_c=round(random.uniform(15, 32), 1),
                    humidity_percent=round(random.uniform(40, 75), 1),
                    noise_db=round(random.uniform(48, 72) + cong * 10, 1),
                ))

        db.commit()

        print("Seeding sensors...")
        sensor_types = ["electricity", "water", "traffic", "air_quality", "noise"]
        for z in zones:
            for st in sensor_types:
                for _ in range(3):
                    db.add(SensorData(
                        zone_id=z.id,
                        sensor_type=st,
                        timestamp=now - timedelta(minutes=random.randint(1, 120)),
                        value=round(random.uniform(10, 500), 2),
                        unit={"electricity": "kWh", "water": "L", "traffic": "veh/hr"}.get(st, "index"),
                        status=random.choice(["active"] * 9 + ["failed"]),
                    ))
        db.commit()

        print("Running ML predictions...")
        for z in zones[:5]:
            elec_vals = [
                r.consumption_kwh
                for r in db.query(ElectricityUsage)
                .filter(ElectricityUsage.zone_id == z.id)
                .order_by(ElectricityUsage.timestamp)
                .limit(168)
                .all()
            ]
            fc = forecast.fit_predict(elec_vals)
            db.add(AIPrediction(
                zone_id=z.id,
                prediction_type=PredictionType.ELECTRICITY,
                predicted_value=fc["predictions"][0],
                confidence_score=fc["confidence"],
                model_name=fc["model_name"],
            ))

        for ptype in [PredictionType.TRAFFIC, PredictionType.WATER, PredictionType.ENVIRONMENT]:
            db.add(AIPrediction(
                prediction_type=ptype,
                predicted_value=round(random.uniform(0.4, 0.8) if ptype == PredictionType.TRAFFIC else random.uniform(50000, 200000), 2),
                confidence_score=round(random.uniform(0.75, 0.95), 3),
                model_name="xgboost",
            ))
        db.commit()

        print("Seeding alerts and optimizations...")
        alert_templates = [
            (AlertType.ELECTRICITY, AlertPriority.HIGH, "Abnormal energy spike detected", "Sector consumption 47% above baseline"),
            (AlertType.TRAFFIC, AlertPriority.MEDIUM, "Traffic overload on main corridor", "Congestion index exceeded 0.85 threshold"),
            (AlertType.WATER, AlertPriority.CRITICAL, "Potential water leak detected", "Leak probability model flagged anomaly"),
            (AlertType.POLLUTION, AlertPriority.MEDIUM, "AQI rising rapidly", "Air quality index crossed 100 in zone"),
            (AlertType.SENSOR, AlertPriority.LOW, "Sensor communication failure", "IoT node offline for 15+ minutes"),
        ]
        for i, (atype, priority, title, msg) in enumerate(alert_templates):
            db.add(Alert(
                zone_id=zones[i % len(zones)].id,
                alert_type=atype,
                priority=priority,
                title=title,
                message=msg,
                is_resolved=i > 2,
            ))

        opt_engine = OptimizationEngine()
        zone_data = [{"id": z.id, "name": z.name, "current_demand": 1500, "predicted_demand": 1620, "efficiency_score": z.efficiency_score} for z in zones]
        for rec in opt_engine.optimize_energy_allocation(zone_data, sum(z["predicted_demand"] for z in zone_data) * 0.9)[:4]:
            db.add(OptimizationLog(
                zone_id=rec.get("zone_id"),
                resource_type=rec["resource_type"],
                recommendation=rec["recommendation"],
                expected_savings_percent=rec["expected_savings_percent"],
                priority=rec["priority"],
            ))

        db.add(OptimizationLog(
            zone_id=zones[5].id,
            resource_type="traffic",
            recommendation="Optimize traffic signal timing at Park Street intersection: reduce cycle from 85s to 64s during peak hours",
            expected_savings_percent=22.5,
            priority="high",
        ))
        db.add(OptimizationLog(
            zone_id=zones[1].id,
            resource_type="water",
            recommendation="Increase water pressure in North Harbor from 38 to 48 PSI for demand spike",
            expected_savings_percent=8.0,
            priority="medium",
        ))

        for component in ["ml-engine", "api-gateway", "sensor-hub", "optimization-engine"]:
            db.add(SystemLog(level="info", component=component, message=f"{component} operational — all systems nominal"))

        db.commit()
        print("Seed complete!")
        print("\nDemo accounts:")
        for email, _, _, pwd in DEMO_USERS:
            print(f"  {email} / {pwd}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
