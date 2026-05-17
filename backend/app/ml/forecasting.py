import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor


class ForecastEngine:
    """Time-series forecasting with XGBoost and gradient boosting fallback."""

    def __init__(self, horizon: int = 24):
        self.horizon = horizon
        self.scaler = StandardScaler()

    def _build_features(self, series: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        n = len(series)
        if n < 48:
            return np.array([]), np.array([])
        X, y = [], []
        for i in range(24, n):
            window = series[i - 24 : i]
            hour_feat = i % 24
            day_feat = (i // 24) % 7
            X.append(np.concatenate([window, [hour_feat, day_feat]]))
            y.append(series[i])
        return np.array(X), np.array(y)

    def fit_predict(self, values: list[float]) -> dict:
        series = np.array(values, dtype=float)
        if len(series) < 48:
            return self._simple_forecast(series)

        X, y = self._build_features(series)
        if len(X) < 10:
            return self._simple_forecast(series)

        X_scaled = self.scaler.fit_transform(X)
        try:
            model = XGBRegressor(
                n_estimators=80,
                max_depth=5,
                learning_rate=0.1,
                random_state=42,
                verbosity=0,
            )
            model.fit(X_scaled, y)
            model_name = "xgboost"
        except Exception:
            model = GradientBoostingRegressor(n_estimators=50, random_state=42)
            model.fit(X_scaled, y)
            model_name = "gradient_boosting"

        predictions = []
        last_window = series[-24:].tolist()
        for h in range(self.horizon):
            hour_feat = (len(series) + h) % 24
            day_feat = ((len(series) + h) // 24) % 7
            feat = np.array(last_window + [hour_feat, day_feat]).reshape(1, -1)
            feat_scaled = self.scaler.transform(feat)
            pred = float(model.predict(feat_scaled)[0])
            predictions.append(pred)
            last_window = last_window[1:] + [pred]

        residuals = y - model.predict(X_scaled)
        std = float(np.std(residuals)) if len(residuals) > 0 else series.std() * 0.1
        confidence = max(0.55, min(0.98, 1.0 - std / (np.mean(np.abs(y)) + 1e-6)))

        return {
            "predictions": predictions,
            "confidence": round(confidence, 3),
            "model_name": model_name,
            "lower_bound": [p - 1.96 * std for p in predictions],
            "upper_bound": [p + 1.96 * std for p in predictions],
        }

    def _simple_forecast(self, series: np.ndarray) -> dict:
        if len(series) == 0:
            base = 100.0
        else:
            base = float(np.mean(series[-min(24, len(series)) :]))
        trend = 0.0
        if len(series) > 1:
            trend = (series[-1] - series[0]) / len(series)
        preds = [base + trend * (i + 1) for i in range(self.horizon)]
        return {
            "predictions": preds,
            "confidence": 0.65,
            "model_name": "moving_average",
            "lower_bound": [p * 0.9 for p in preds],
            "upper_bound": [p * 1.1 for p in preds],
        }
