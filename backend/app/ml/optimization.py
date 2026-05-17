import numpy as np
from scipy.optimize import linprog


class OptimizationEngine:
    """Generate resource allocation and traffic signal optimization recommendations."""

    def optimize_energy_allocation(
        self,
        zones: list[dict],
        total_budget_kwh: float,
    ) -> list[dict]:
        n = len(zones)
        if n == 0:
            return []

        demands = np.array([z.get("predicted_demand", z.get("current_demand", 100)) for z in zones])
        efficiencies = np.array([z.get("efficiency_score", 75) / 100 for z in zones])
        costs = 1.0 / (efficiencies + 0.1)

        c = costs
        A_ub = [demands]
        b_ub = [total_budget_kwh]
        bounds = [(0, d * 1.2) for d in demands]

        try:
            result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")
            allocations = result.x if result.success else demands * (total_budget_kwh / demands.sum())
        except Exception:
            allocations = demands * (total_budget_kwh / (demands.sum() + 1e-6))

        recommendations = []
        for zone, alloc, demand in zip(zones, allocations, demands):
            diff = demand - alloc
            if diff > demand * 0.15:
                recommendations.append({
                    "zone_id": zone.get("id"),
                    "zone_name": zone.get("name", "Unknown"),
                    "resource_type": "electricity",
                    "recommendation": (
                        f"Reduce energy allocation in {zone.get('name', 'sector')} "
                        f"during low demand hours by {diff:.0f} kWh"
                    ),
                    "expected_savings_percent": round(min(25, diff / demand * 100), 1),
                    "priority": "high" if diff > demand * 0.25 else "medium",
                })
            elif alloc > demand * 1.1:
                recommendations.append({
                    "zone_id": zone.get("id"),
                    "zone_name": zone.get("name", "Unknown"),
                    "resource_type": "electricity",
                    "recommendation": (
                        f"Increase renewable allocation in {zone.get('name', 'sector')} "
                        f"by {(alloc - demand):.0f} kWh for peak readiness"
                    ),
                    "expected_savings_percent": 5.0,
                    "priority": "low",
                })
        return recommendations

    def optimize_traffic_signals(
        self,
        intersections: list[dict],
    ) -> list[dict]:
        recommendations = []
        for inter in intersections:
            congestion = inter.get("congestion", 0.5)
            wait = inter.get("signal_wait_seconds", 60)
            if congestion > 0.7 and wait > 45:
                new_wait = max(30, wait * 0.75)
                recommendations.append({
                    "zone_id": inter.get("zone_id"),
                    "zone_name": inter.get("name", "Intersection"),
                    "resource_type": "traffic",
                    "recommendation": (
                        f"Optimize traffic signal timing at {inter.get('name', 'intersection')}: "
                        f"reduce cycle from {wait:.0f}s to {new_wait:.0f}s during peak hours"
                    ),
                    "expected_savings_percent": round((wait - new_wait) / wait * 30, 1),
                    "priority": "high" if congestion > 0.85 else "medium",
                })
        return recommendations

    def optimize_water_pressure(
        self,
        zones: list[dict],
    ) -> list[dict]:
        recommendations = []
        for zone in zones:
            pressure = zone.get("pressure_psi", 45)
            leak_prob = zone.get("leak_probability", 0)
            demand = zone.get("predicted_demand", zone.get("consumption", 0))

            if leak_prob > 0.6:
                recommendations.append({
                    "zone_id": zone.get("id"),
                    "zone_name": zone.get("name", "Zone"),
                    "resource_type": "water",
                    "recommendation": (
                        f"Investigate potential leak in {zone.get('name')}: "
                        f"leak probability {leak_prob * 100:.0f}%"
                    ),
                    "expected_savings_percent": 18.0,
                    "priority": "critical" if leak_prob > 0.8 else "high",
                })
            elif pressure < 40 and demand > zone.get("avg_demand", demand) * 1.1:
                recommendations.append({
                    "zone_id": zone.get("id"),
                    "zone_name": zone.get("name", "Zone"),
                    "resource_type": "water",
                    "recommendation": (
                        f"Increase water pressure in {zone.get('name')} "
                        f"from {pressure:.0f} to 48 PSI for demand spike"
                    ),
                    "expected_savings_percent": 8.0,
                    "priority": "medium",
                })
        return recommendations

    def city_efficiency_score(
        self,
        electricity_eff: float,
        traffic_score: float,
        water_eff: float,
        aqi_score: float,
    ) -> float:
        weights = [0.3, 0.25, 0.25, 0.2]
        scores = [
            min(100, electricity_eff),
            max(0, 100 - traffic_score * 100),
            min(100, water_eff),
            max(0, 100 - aqi_score),
        ]
        return round(sum(w * s for w, s in zip(weights, scores)), 1)
