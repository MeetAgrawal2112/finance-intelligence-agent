# app/services/anomaly_service.py
import joblib
import numpy as np
import os
from datetime import datetime, timezone
from typing import Optional

class AnomalyService:
    """
    Singleton — model ek baar load, baar baar use.
    3-layer detection:
    1. Isolation Forest (ML-based)
    2. Z-Score (statistical)
    3. Rule-based (business logic)
    """
    _instance = None
    _model_data = None

    # User ke historical stats (in-memory cache)
    # Production mein Redis ya DB mein store hoga
    _user_stats: dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> bool:
        model_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../ml/models/anomaly_detector.pkl"
            )
        )

        if not os.path.exists(model_path):
            print(f"⚠️  Anomaly model not found: {model_path}")
            return False

        try:
            self._model_data = joblib.load(model_path)
            print(f"✅ Anomaly detector loaded")
            return True
        except Exception as e:
            print(f"❌ Failed to load anomaly detector: {e}")
            return False

    def _extract_features(self, amount: float,
                          transaction_date: datetime) -> np.ndarray:
        """Transaction se features nikalo."""
        hour = transaction_date.hour
        dow = transaction_date.weekday()

        return np.array([[
            amount,
            np.log1p(amount),
            hour,
            dow,
            1 if dow >= 5 else 0,
            1 if hour >= 23 or hour <= 5 else 0,
        ]])

    def _isolation_forest_score(self, features: np.ndarray) -> float:
        """Isolation Forest se anomaly score."""
        if not self._model_data:
            return 0.0

        scaler = self._model_data["scaler"]
        iso_forest = self._model_data["iso_forest"]

        scaled = scaler.transform(features)
        raw_score = iso_forest.score_samples(scaled)[0]

        # Normalize to 0-1
        return float(max(0, min(1, (-raw_score - 0.3) / 0.7)))

    def _zscore_score(self, amount: float,
                      user_id: str, category: str) -> float:
        """
        Z-Score: kitna standard deviations average se door hai?
        |z| > 2 → suspicious
        |z| > 3 → very suspicious
        """
        key = f"{user_id}:{category}"
        stats = self._user_stats.get(key)

        if not stats or stats.get('count', 0) < 5:
            # History nahi hai — can't compute z-score
            return 0.0

        mean = stats['mean']
        std = stats.get('std', mean * 0.3)

        if std == 0:
            return 0.0

        z = abs(amount - mean) / std

        # Z-score to 0-1 score
        if z < 1.5:
            return 0.0
        elif z < 2.0:
            return 0.2
        elif z < 2.5:
            return 0.4
        elif z < 3.0:
            return 0.6
        else:
            return min(1.0, 0.7 + (z - 3.0) * 0.1)

    def _rule_based_score(self, amount: float,
                          description: str,
                          transaction_date: datetime,
                          user_id: str) -> tuple[float, list[str]]:
        """
        Business rules se anomaly check.
        Returns (score, list of reasons)
        """
        score = 0.0
        reasons = []

        # Rule 1: Bahut bada amount
        if amount > 50000:
            score = max(score, 0.8)
            reasons.append(f"Very large amount: ₹{amount:,.0f}")
        elif amount > 20000:
            score = max(score, 0.5)
            reasons.append(f"Large amount: ₹{amount:,.0f}")
        elif amount > 10000:
            score = max(score, 0.3)
            reasons.append(f"High amount: ₹{amount:,.0f}")

        # Rule 2: Raat ka transaction (12am-5am)
        hour = transaction_date.hour
        if 0 <= hour <= 5:
            score = max(score, 0.4)
            reasons.append(f"Odd hour transaction: {hour}:00 AM")

        # Rule 3: Round number (potential manual fraud)
        if amount >= 1000 and amount % 1000 == 0 and amount > 5000:
            score = max(score, 0.2)
            reasons.append(f"Suspiciously round amount: ₹{amount:,.0f}")

        # Rule 4: International keywords
        intl_keywords = ['international', 'foreign', 'usd', 'eur', 'gbp',
                        'dollar', 'euro', 'pound']
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in intl_keywords):
            score = max(score, 0.3)
            reasons.append("International transaction detected")

        return score, reasons

    def analyze_transaction(
        self,
        amount: float,
        description: str,
        transaction_date: datetime,
        user_id: str,
        category: str = "Other"
    ) -> dict:
        """
        Transaction analyze karo — combined anomaly score.

        Returns:
        {
            "is_anomaly": bool,
            "anomaly_score": float (0-1),
            "severity": "low/medium/high",
            "reasons": [...],
            "scores": {
                "isolation_forest": float,
                "z_score": float,
                "rule_based": float
            }
        }
        """
        # Features extract karo
        features = self._extract_features(amount, transaction_date)

        # 3 scores calculate karo
        if_score = self._isolation_forest_score(features)
        z_score = self._zscore_score(amount, user_id, category)
        rule_score, reasons = self._rule_based_score(
            amount, description, transaction_date, user_id
        )

        # Weighted combined score
        # Rule-based sabse important (0.4), phir IF (0.35), phir Z-score (0.25)
        combined_score = (
            if_score * 0.35 +
            z_score * 0.25 +
            rule_score * 0.40
        )
        combined_score = round(min(1.0, combined_score), 3)

        # Threshold
        threshold = 0.5
        is_anomaly = combined_score >= threshold

        # Severity
        if combined_score >= 0.75:
            severity = "high"
        elif combined_score >= 0.5:
            severity = "medium"
        else:
            severity = "low"

        # User stats update karo
        self._update_user_stats(user_id, category, amount)

        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": combined_score,
            "severity": severity,
            "reasons": reasons if reasons else ["No specific anomaly pattern"],
            "scores": {
                "isolation_forest": round(if_score, 3),
                "z_score": round(z_score, 3),
                "rule_based": round(rule_score, 3),
            }
        }

    def _update_user_stats(self, user_id: str,
                           category: str, amount: float):
        """
        Running mean aur std update karo.
        Welford's online algorithm use karta hai —
        poora history store karne ki zaroorat nahi.
        """
        key = f"{user_id}:{category}"

        if key not in self._user_stats:
            self._user_stats[key] = {
                'count': 0, 'mean': 0.0,
                'M2': 0.0, 'std': 0.0
            }

        stats = self._user_stats[key]
        stats['count'] += 1
        n = stats['count']

        # Welford's algorithm
        delta = amount - stats['mean']
        stats['mean'] += delta / n
        delta2 = amount - stats['mean']
        stats['M2'] += delta * delta2

        if n >= 2:
            stats['std'] = (stats['M2'] / (n - 1)) ** 0.5

    def load_user_history(self, user_id: str,
                          transactions: list):
        """
        User ki existing transactions se stats build karo.
        User login pe call karo.
        """
        for txn in transactions:
            self._update_user_stats(
                user_id,
                txn.get('category', 'Other'),
                txn.get('amount', 0)
            )

    @property
    def is_loaded(self) -> bool:
        return self._model_data is not None

# Global instance
anomaly_detector = AnomalyService()