import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class ZoneClusterer:
    """Cluster city zones by resource usage patterns."""

    def cluster_zones(
        self,
        zone_features: list[dict],
        n_clusters: int = 3,
    ) -> list[dict]:
        if len(zone_features) < n_clusters:
            return [
                {**z, "cluster_id": i, "cluster_label": f"Group {i + 1}"}
                for i, z in enumerate(zone_features)
            ]

        feature_matrix = np.array([
            [
                z.get("electricity", 0),
                z.get("water", 0),
                z.get("congestion", 0),
                z.get("aqi", 0),
            ]
            for z in zone_features
        ])

        scaler = StandardScaler()
        scaled = scaler.fit_transform(feature_matrix)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(scaled)

        cluster_names = {
            0: "High Demand",
            1: "Balanced",
            2: "Efficient",
        }

        results = []
        for zone, label in zip(zone_features, labels):
            results.append({
                **zone,
                "cluster_id": int(label),
                "cluster_label": cluster_names.get(int(label), f"Cluster {label + 1}"),
            })
        return results
