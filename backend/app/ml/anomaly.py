import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    """Isolation Forest based anomaly detection for utility metrics."""

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
        )
        self.scaler = StandardScaler()

    def detect(self, values: list[float], timestamps: list | None = None) -> list[dict]:
        if len(values) < 20:
            return []

        X = np.array(values).reshape(-1, 1)
        if len(values) >= 48:
            rolling_mean = pd_rolling_mean(values, 12)
            rolling_std = pd_rolling_std(values, 12)
            hour_idx = np.array([i % 24 for i in range(len(values))]).reshape(-1, 1)
            X = np.hstack([X, rolling_mean.reshape(-1, 1), rolling_std.reshape(-1, 1), hour_idx])

        X_scaled = self.scaler.fit_transform(X)
        labels = self.model.fit_predict(X_scaled)
        scores = self.model.decision_function(X_scaled)

        anomalies = []
        for i, (label, score) in enumerate(zip(labels, scores)):
            if label == -1:
                anomalies.append({
                    "index": i,
                    "value": values[i],
                    "anomaly_score": round(float(-score), 4),
                    "timestamp": timestamps[i] if timestamps else None,
                    "severity": "high" if score < -0.3 else "medium",
                })
        return anomalies


def pd_rolling_mean(values: list[float], window: int) -> np.ndarray:
    arr = np.array(values, dtype=float)
    result = np.zeros_like(arr)
    for i in range(len(arr)):
        start = max(0, i - window + 1)
        result[i] = np.mean(arr[start : i + 1])
    return result


def pd_rolling_std(values: list[float], window: int) -> np.ndarray:
    arr = np.array(values, dtype=float)
    result = np.zeros_like(arr)
    for i in range(len(arr)):
        start = max(0, i - window + 1)
        result[i] = np.std(arr[start : i + 1]) + 1e-6
    return result
