from datetime import datetime, timedelta
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from app.models.city import (
    CityZone,
    ElectricityUsage,
    WaterUsage,
    TrafficData,
    EnvironmentalData,
    Alert,
    OptimizationLog,
    SystemLog,
    AIPrediction,
)
from app.models.city import AlertType
from app.ml.forecasting import ForecastEngine
from app.ml.anomaly import AnomalyDetector
from app.ml.optimization import OptimizationEngine
from app.ml.clustering import ZoneClusterer


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.forecast = ForecastEngine(horizon=24)
        self.anomaly = AnomalyDetector()
        self.optimizer = OptimizationEngine()
        self.clusterer = ZoneClusterer()

    def get_dashboard_overview(self) -> dict:
        since = datetime.utcnow() - timedelta(hours=24)
        elec = (
            self.db.query(func.sum(ElectricityUsage.consumption_kwh))
            .filter(ElectricityUsage.timestamp >= since)
            .scalar()
            or 0
        )
        water = (
            self.db.query(func.sum(WaterUsage.consumption_liters))
            .filter(WaterUsage.timestamp >= since)
            .scalar()
            or 0
        )
        traffic = (
            self.db.query(func.avg(TrafficData.congestion_level))
            .filter(TrafficData.timestamp >= since)
            .scalar()
            or 0.5
        )
        aqi = (
            self.db.query(func.avg(EnvironmentalData.aqi))
            .filter(EnvironmentalData.timestamp >= since)
            .scalar()
            or 50
        )
        zones = self.db.query(CityZone).all()
        eff_scores = [z.efficiency_score for z in zones] or [75]
        energy_eff = sum(eff_scores) / len(eff_scores)
        carbon = sum(z.carbon_estimate_tons for z in zones)
        active_alerts = (
            self.db.query(func.count(Alert.id))
            .filter(Alert.is_resolved == False)
            .scalar()
            or 0
        )
        city_score = self.optimizer.city_efficiency_score(
            energy_eff, float(traffic), energy_eff * 0.95, float(aqi) / 2
        )
        recommendations = (
            self.db.query(OptimizationLog)
            .order_by(OptimizationLog.created_at.desc())
            .limit(5)
            .all()
        )
        zone_map = {z.id: z.name for z in zones}
        rec_items = [
            {
                "id": r.id,
                "resource_type": r.resource_type,
                "recommendation": r.recommendation,
                "expected_savings_percent": r.expected_savings_percent,
                "priority": r.priority,
                "zone_name": zone_map.get(r.zone_id) if r.zone_id else None,
            }
            for r in recommendations
        ]
        activity = (
            self.db.query(SystemLog)
            .order_by(SystemLog.created_at.desc())
            .limit(8)
            .all()
        )
        rankings = sorted(
            [
                {
                    "zone_id": z.id,
                    "name": z.name,
                    "sector_code": z.sector_code,
                    "efficiency_score": z.efficiency_score,
                    "rank": 0,
                }
                for z in zones
            ],
            key=lambda x: x["efficiency_score"],
            reverse=True,
        )
        for i, r in enumerate(rankings):
            r["rank"] = i + 1

        return {
            "electricity_kwh": round(float(elec), 1),
            "traffic_congestion": round(float(traffic), 3),
            "water_liters": round(float(water), 0),
            "air_quality_index": round(float(aqi), 1),
            "energy_efficiency_score": round(energy_eff, 1),
            "city_efficiency_score": city_score,
            "active_alerts": active_alerts,
            "carbon_emission_tons": round(carbon, 2),
            "metrics": [
                {"label": "Electricity", "value": float(elec), "unit": "kWh", "change_percent": 2.4, "trend": "up"},
                {"label": "Traffic Load", "value": float(traffic) * 100, "unit": "%", "change_percent": -1.2, "trend": "down"},
                {"label": "Water", "value": float(water), "unit": "L", "change_percent": 0.8, "trend": "up"},
                {"label": "Air Quality", "value": float(aqi), "unit": "AQI", "change_percent": -3.1, "trend": "down"},
            ],
            "recommendations": rec_items,
            "recent_activity": [
                {
                    "id": a.id,
                    "message": a.message,
                    "component": a.component,
                    "level": a.level,
                    "created_at": a.created_at,
                }
                for a in activity
            ],
            "district_rankings": rankings[:8],
        }

    def get_map_zones(self) -> list[dict]:
        since = datetime.utcnow() - timedelta(hours=6)
        zones = self.db.query(CityZone).all()
        result = []
        for z in zones:
            elec = (
                self.db.query(func.avg(ElectricityUsage.consumption_kwh))
                .filter(ElectricityUsage.zone_id == z.id, ElectricityUsage.timestamp >= since)
                .scalar()
                or 0
            )
            water = (
                self.db.query(func.avg(WaterUsage.consumption_liters))
                .filter(WaterUsage.zone_id == z.id, WaterUsage.timestamp >= since)
                .scalar()
                or 0
            )
            cong = (
                self.db.query(func.avg(TrafficData.congestion_level))
                .filter(TrafficData.zone_id == z.id, TrafficData.timestamp >= since)
                .scalar()
                or 0.3
            )
            aqi = (
                self.db.query(func.avg(EnvironmentalData.aqi))
                .filter(EnvironmentalData.zone_id == z.id, EnvironmentalData.timestamp >= since)
                .scalar()
                or 50
            )
            alerts = (
                self.db.query(func.count(Alert.id))
                .filter(Alert.zone_id == z.id, Alert.is_resolved == False)
                .scalar()
                or 0
            )
            result.append({
                "id": z.id,
                "name": z.name,
                "sector_code": z.sector_code,
                "latitude": z.latitude,
                "longitude": z.longitude,
                "electricity_kwh": round(float(elec), 1),
                "water_liters": round(float(water), 0),
                "congestion": round(float(cong), 3),
                "aqi": round(float(aqi), 1),
                "efficiency_score": z.efficiency_score,
                "alert_count": alerts,
            })
        return result

    def _hourly_series(self, model, zone_id: int | None, value_field: str, hours: int = 48):
        since = datetime.utcnow() - timedelta(hours=hours)
        q = self.db.query(model).filter(model.timestamp >= since)
        if zone_id:
            q = q.filter(model.zone_id == zone_id)
        records = q.order_by(model.timestamp).all()
        by_hour: dict[str, list[float]] = {}
        for r in records:
            key = r.timestamp.strftime("%Y-%m-%d %H:00")
            val = getattr(r, value_field)
            by_hour.setdefault(key, []).append(val)
        return [{"hour": k, "value": round(sum(v) / len(v), 2)} for k, v in sorted(by_hour.items())]

    def electricity_analytics(self, zone_id: int | None = None) -> dict:
        since = datetime.utcnow() - timedelta(days=7)
        q = self.db.query(ElectricityUsage).filter(ElectricityUsage.timestamp >= since)
        if zone_id:
            q = q.filter(ElectricityUsage.zone_id == zone_id)
        records = q.order_by(ElectricityUsage.timestamp).all()
        values = [r.consumption_kwh for r in records]
        timestamps = [r.timestamp.isoformat() for r in records]
        forecast_result = self.forecast.fit_predict(values[-336:] if len(values) > 336 else values)
        anomalies = self.anomaly.detect(values[-168:], timestamps[-168:] if timestamps else None)

        district = self.db.execute(
            text("""
                SELECT z.name, z.sector_code, AVG(e.consumption_kwh) as avg_kwh,
                       SUM(e.consumption_kwh) as total_kwh,
                       COUNT(CASE WHEN e.is_anomaly THEN 1 END) as anomaly_count
                FROM city_zones z
                JOIN electricity_usage e ON e.zone_id = z.id
                WHERE e.timestamp >= :since
                GROUP BY z.id, z.name, z.sector_code
                ORDER BY total_kwh DESC
            """),
            {"since": since},
        ).fetchall()

        return {
            "summary": {
                "total_kwh": round(sum(values), 1) if values else 0,
                "avg_hourly": round(sum(values) / max(len(values), 1), 2),
                "anomaly_count": len(anomalies),
                "forecast_confidence": forecast_result["confidence"],
            },
            "hourly_series": self._hourly_series(ElectricityUsage, zone_id, "consumption_kwh"),
            "district_breakdown": [
                {
                    "name": row[0],
                    "sector_code": row[1],
                    "avg_kwh": round(float(row[2]), 1),
                    "total_kwh": round(float(row[3]), 1),
                    "anomaly_count": int(row[4]),
                }
                for row in district
            ],
            "forecasts": [
                {
                    "timestamp": (datetime.utcnow() + timedelta(hours=i + 1)).isoformat(),
                    "actual": None,
                    "predicted": round(p, 2),
                    "lower_bound": round(forecast_result["lower_bound"][i], 2),
                    "upper_bound": round(forecast_result["upper_bound"][i], 2),
                }
                for i, p in enumerate(forecast_result["predictions"][:24])
            ],
            "anomalies": anomalies[-10:],
            "recommendations": self._energy_recommendations(),
        }

    def traffic_analytics(self, zone_id: int | None = None) -> dict:
        since = datetime.utcnow() - timedelta(days=7)
        q = self.db.query(TrafficData).filter(TrafficData.timestamp >= since)
        if zone_id:
            q = q.filter(TrafficData.zone_id == zone_id)
        records = q.order_by(TrafficData.timestamp).all()
        values = [r.congestion_level for r in records]
        forecast_result = self.forecast.fit_predict(values[-336:] if len(values) > 336 else values)

        zones = self.db.query(CityZone).all()
        intersections = []
        for z in zones:
            latest = (
                self.db.query(TrafficData)
                .filter(TrafficData.zone_id == z.id)
                .order_by(TrafficData.timestamp.desc())
                .first()
            )
            if latest:
                intersections.append({
                    "zone_id": z.id,
                    "name": z.name,
                    "congestion": latest.congestion_level,
                    "signal_wait_seconds": latest.signal_wait_seconds,
                    "accident_risk": latest.accident_risk_score,
                })

        zone_features = []
        for z in zones:
            elec = self.db.query(func.avg(ElectricityUsage.consumption_kwh)).filter(
                ElectricityUsage.zone_id == z.id
            ).scalar() or 0
            water = self.db.query(func.avg(WaterUsage.consumption_liters)).filter(
                WaterUsage.zone_id == z.id
            ).scalar() or 0
            cong = self.db.query(func.avg(TrafficData.congestion_level)).filter(
                TrafficData.zone_id == z.id
            ).scalar() or 0
            aqi = self.db.query(func.avg(EnvironmentalData.aqi)).filter(
                EnvironmentalData.zone_id == z.id
            ).scalar() or 50
            zone_features.append({
                "id": z.id,
                "name": z.name,
                "electricity": float(elec),
                "water": float(water),
                "congestion": float(cong),
                "aqi": float(aqi),
            })
        clusters = self.clusterer.cluster_zones(zone_features)
        traffic_recs = self.optimizer.optimize_traffic_signals(intersections)

        return {
            "summary": {
                "avg_congestion": round(sum(values) / max(len(values), 1), 3) if values else 0,
                "peak_congestion": round(max(values), 3) if values else 0,
                "forecast_confidence": forecast_result["confidence"],
            },
            "hourly_series": self._hourly_series(TrafficData, zone_id, "congestion_level"),
            "district_breakdown": clusters,
            "forecasts": [
                {
                    "timestamp": (datetime.utcnow() + timedelta(hours=i + 1)).isoformat(),
                    "actual": None,
                    "predicted": round(p, 3),
                }
                for i, p in enumerate(forecast_result["predictions"][:24])
            ],
            "anomalies": [],
            "recommendations": [r["recommendation"] for r in traffic_recs[:5]],
            "accident_hotspots": sorted(intersections, key=lambda x: x.get("accident_risk", 0), reverse=True)[:5],
        }

    def water_analytics(self, zone_id: int | None = None) -> dict:
        since = datetime.utcnow() - timedelta(days=7)
        q = self.db.query(WaterUsage).filter(WaterUsage.timestamp >= since)
        if zone_id:
            q = q.filter(WaterUsage.zone_id == zone_id)
        records = q.order_by(WaterUsage.timestamp).all()
        values = [r.consumption_liters for r in records]
        timestamps = [r.timestamp.isoformat() for r in records]
        forecast_result = self.forecast.fit_predict(values[-336:] if len(values) > 336 else values)
        anomalies = self.anomaly.detect(values[-168:], timestamps[-168:] if timestamps else None)

        zones = self.db.query(CityZone).all()
        water_zones = []
        for z in zones:
            latest = (
                self.db.query(WaterUsage)
                .filter(WaterUsage.zone_id == z.id)
                .order_by(WaterUsage.timestamp.desc())
                .first()
            )
            if latest:
                avg = self.db.query(func.avg(WaterUsage.consumption_liters)).filter(
                    WaterUsage.zone_id == z.id
                ).scalar() or latest.consumption_liters
                water_zones.append({
                    "id": z.id,
                    "name": z.name,
                    "pressure_psi": latest.pressure_psi,
                    "leak_probability": latest.leak_probability,
                    "consumption": latest.consumption_liters,
                    "avg_demand": float(avg),
                    "predicted_demand": latest.consumption_liters * 1.05,
                })

        water_recs = self.optimizer.optimize_water_pressure(water_zones)

        return {
            "summary": {
                "total_liters": round(sum(values), 0) if values else 0,
                "leak_alerts": sum(1 for z in water_zones if z.get("leak_probability", 0) > 0.5),
                "forecast_confidence": forecast_result["confidence"],
            },
            "hourly_series": self._hourly_series(WaterUsage, zone_id, "consumption_liters"),
            "district_breakdown": water_zones,
            "forecasts": [
                {
                    "timestamp": (datetime.utcnow() + timedelta(hours=i + 1)).isoformat(),
                    "actual": None,
                    "predicted": round(p, 0),
                }
                for i, p in enumerate(forecast_result["predictions"][:24])
            ],
            "anomalies": anomalies[-10:],
            "recommendations": [r["recommendation"] for r in water_recs[:5]],
        }

    def _energy_recommendations(self) -> list[str]:
        zones = self.db.query(CityZone).all()
        zone_data = []
        for z in zones:
            demand = (
                self.db.query(func.avg(ElectricityUsage.consumption_kwh))
                .filter(ElectricityUsage.zone_id == z.id)
                .scalar()
                or 100
            )
            zone_data.append({
                "id": z.id,
                "name": z.name,
                "current_demand": float(demand),
                "predicted_demand": float(demand) * 1.08,
                "efficiency_score": z.efficiency_score,
            })
        total = sum(z["predicted_demand"] for z in zone_data) * 0.95
        recs = self.optimizer.optimize_energy_allocation(zone_data, total)
        return [r["recommendation"] for r in recs[:5]]

    def sql_analytics_report(self) -> dict:
        dialect = self.db.bind.dialect.name if self.db.bind else "postgresql"
        if dialect == "sqlite":
            return self._sql_analytics_report_sqlite()
        reports = {}
        reports["district_energy"] = [
            dict(row._mapping)
            for row in self.db.execute(text("""
                SELECT z.name, z.sector_code,
                       ROUND(AVG(e.consumption_kwh)::numeric, 2) as avg_kwh,
                       ROUND(SUM(e.consumption_kwh)::numeric, 2) as total_kwh
                FROM city_zones z
                JOIN electricity_usage e ON e.zone_id = z.id
                WHERE e.timestamp >= NOW() - INTERVAL '30 days'
                GROUP BY z.id, z.name, z.sector_code
                ORDER BY total_kwh DESC
            """)).fetchall()
        ]
        reports["traffic_trends"] = [
            dict(row._mapping)
            for row in self.db.execute(text("""
                SELECT DATE_TRUNC('day', t.timestamp) as day,
                       ROUND(AVG(t.congestion_level)::numeric, 3) as avg_congestion,
                       ROUND(MAX(t.congestion_level)::numeric, 3) as peak_congestion
                FROM traffic_data t
                WHERE t.timestamp >= NOW() - INTERVAL '14 days'
                GROUP BY day ORDER BY day
            """)).fetchall()
        ]
        reports["water_stats"] = [
            dict(row._mapping)
            for row in self.db.execute(text("""
                SELECT z.name,
                       ROUND(AVG(w.consumption_liters)::numeric, 0) as avg_liters,
                       ROUND(AVG(w.leak_probability)::numeric, 3) as avg_leak_risk
                FROM city_zones z
                JOIN water_usage w ON w.zone_id = z.id
                WHERE w.timestamp >= NOW() - INTERVAL '7 days'
                GROUP BY z.id, z.name
            """)).fetchall()
        ]
        reports["prediction_accuracy"] = [
            dict(row._mapping)
            for row in self.db.execute(text("""
                SELECT prediction_type, model_name,
                       COUNT(*) as prediction_count,
                       ROUND(AVG(confidence_score)::numeric, 3) as avg_confidence
                FROM ai_predictions
                WHERE created_at >= NOW() - INTERVAL '7 days'
                GROUP BY prediction_type, model_name
            """)).fetchall()
        ]
        reports["anomaly_frequency"] = [
            dict(row._mapping)
            for row in self.db.execute(text("""
                SELECT 'electricity' as resource,
                       COUNT(*) FILTER (WHERE is_anomaly) as anomalies,
                       COUNT(*) as total_records
                FROM electricity_usage WHERE timestamp >= NOW() - INTERVAL '7 days'
                UNION ALL
                SELECT 'water', COUNT(*) FILTER (WHERE is_anomaly), COUNT(*)
                FROM water_usage WHERE timestamp >= NOW() - INTERVAL '7 days'
            """)).fetchall()
        ]
        return reports

    def _sql_analytics_report_sqlite(self) -> dict:
        def rows(sql: str):
            return [dict(r._mapping) for r in self.db.execute(text(sql)).fetchall()]

        return {
            "district_energy": rows("""
                SELECT z.name, z.sector_code,
                       ROUND(AVG(e.consumption_kwh), 2) as avg_kwh,
                       ROUND(SUM(e.consumption_kwh), 2) as total_kwh
                FROM city_zones z
                JOIN electricity_usage e ON e.zone_id = z.id
                WHERE e.timestamp >= datetime('now', '-30 days')
                GROUP BY z.id, z.name, z.sector_code
                ORDER BY total_kwh DESC
            """),
            "traffic_trends": rows("""
                SELECT date(t.timestamp) as day,
                       ROUND(AVG(t.congestion_level), 3) as avg_congestion,
                       ROUND(MAX(t.congestion_level), 3) as peak_congestion
                FROM traffic_data t
                WHERE t.timestamp >= datetime('now', '-14 days')
                GROUP BY day ORDER BY day
            """),
            "water_stats": rows("""
                SELECT z.name,
                       ROUND(AVG(w.consumption_liters), 0) as avg_liters,
                       ROUND(AVG(w.leak_probability), 3) as avg_leak_risk
                FROM city_zones z
                JOIN water_usage w ON w.zone_id = z.id
                WHERE w.timestamp >= datetime('now', '-7 days')
                GROUP BY z.id, z.name
            """),
            "prediction_accuracy": rows("""
                SELECT prediction_type, model_name,
                       COUNT(*) as prediction_count,
                       ROUND(AVG(confidence_score), 3) as avg_confidence
                FROM ai_predictions
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY prediction_type, model_name
            """),
            "anomaly_frequency": rows("""
                SELECT 'electricity' as resource,
                       SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END) as anomalies,
                       COUNT(*) as total_records
                FROM electricity_usage WHERE timestamp >= datetime('now', '-7 days')
                UNION ALL
                SELECT 'water',
                       SUM(CASE WHEN is_anomaly THEN 1 ELSE 0 END),
                       COUNT(*)
                FROM water_usage WHERE timestamp >= datetime('now', '-7 days')
            """),
        }

    def run_predictions(self) -> list[dict]:
        from app.models.city import PredictionType, AIPrediction

        results = []
        for ptype, model_cls, field in [
            (PredictionType.ELECTRICITY, ElectricityUsage, "consumption_kwh"),
            (PredictionType.TRAFFIC, TrafficData, "congestion_level"),
            (PredictionType.WATER, WaterUsage, "consumption_liters"),
        ]:
            records = (
                self.db.query(model_cls)
                .order_by(model_cls.timestamp.desc())
                .limit(500)
                .all()
            )
            values = [getattr(r, field) for r in reversed(records)]
            fc = self.forecast.fit_predict(values)
            pred = AIPrediction(
                prediction_type=ptype,
                predicted_value=fc["predictions"][0],
                confidence_score=fc["confidence"],
                model_name=fc["model_name"],
                horizon_hours=24,
            )
            self.db.add(pred)
            results.append({
                "type": ptype.value,
                "value": fc["predictions"][0],
                "confidence": fc["confidence"],
            })
        self.db.commit()
        return results

    def generate_optimizations(self) -> int:
        zones = self.db.query(CityZone).all()
        count = 0
        zone_data = []
        for z in zones:
            demand = (
                self.db.query(func.avg(ElectricityUsage.consumption_kwh))
                .filter(ElectricityUsage.zone_id == z.id)
                .scalar()
                or 100
            )
            zone_data.append({
                "id": z.id,
                "name": z.name,
                "current_demand": float(demand),
                "predicted_demand": float(demand) * 1.08,
                "efficiency_score": z.efficiency_score,
            })
        total = sum(z["predicted_demand"] for z in zone_data) * 0.92
        for rec in self.optimizer.optimize_energy_allocation(zone_data, total)[:3]:
            self.db.add(OptimizationLog(
                zone_id=rec.get("zone_id"),
                resource_type=rec["resource_type"],
                recommendation=rec["recommendation"],
                expected_savings_percent=rec["expected_savings_percent"],
                priority=rec["priority"],
            ))
            count += 1

        intersections = []
        for z in zones:
            latest = (
                self.db.query(TrafficData)
                .filter(TrafficData.zone_id == z.id)
                .order_by(TrafficData.timestamp.desc())
                .first()
            )
            if latest:
                intersections.append({
                    "zone_id": z.id,
                    "name": z.name,
                    "congestion": latest.congestion_level,
                    "signal_wait_seconds": latest.signal_wait_seconds,
                })
        for rec in self.optimizer.optimize_traffic_signals(intersections)[:2]:
            self.db.add(OptimizationLog(**{
                "zone_id": rec.get("zone_id"),
                "resource_type": rec["resource_type"],
                "recommendation": rec["recommendation"],
                "expected_savings_percent": rec["expected_savings_percent"],
                "priority": rec["priority"],
            }))
            count += 1

        self.db.commit()
        return count
