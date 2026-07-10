# app/services/prediction_service.py
import joblib
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
))
from ml.forecaster import SimpleForecaster  # ← ADD
from typing import Optional
import warnings
warnings.filterwarnings('ignore')

class PredictionService:
    """
    Spending Prediction Service.
    Prophet models load karke future spending predict karta hai.
    """
    _instance = None
    _model_data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self) -> bool:
        model_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../ml/models/spending_predictor.pkl"
            )
        )

        if not os.path.exists(model_path):
            print(f"⚠️  Prediction model not found: {model_path}")
            return False

        try:
            self._model_data = joblib.load(model_path)
            cats = len(self._model_data.get('categories', []))
            print(f"✅ Spending predictor loaded — {cats} categories")
            return True
        except Exception as e:
            print(f"❌ Failed to load predictor: {e}")
            return False

    def predict_next_month(
        self,
        user_transactions: list = None
    ) -> dict:
        """
        Next 30 days ka category-wise spending predict karo.

        Args:
            user_transactions: User ki actual transactions list
                               (agar available ho toh model retrain hoga)

        Returns:
            {
                "predictions": [
                    {
                        "category": "Groceries",
                        "predicted_amount": 4250.0,
                        "lower_bound": 3800.0,
                        "upper_bound": 4700.0,
                        "trend": "increasing",
                        "confidence": 0.8
                    },
                    ...
                ],
                "total_predicted": 21830.0,
                "forecast_period": "2025-02-01 to 2025-03-02",
                "savings_potential": 2500.0
            }
        """
        if not self._model_data:
            return self._fallback_prediction()

        models = self._model_data["models"]
        categories = self._model_data["categories"]

        predictions = []
        total = 0.0

        today = datetime.now(timezone.utc)
        start_date = today + timedelta(days=1)
        end_date = today + timedelta(days=30)

        for cat in categories:
            if cat not in models:
                continue

            model = models[cat]

            try:
                # Future dataframe banao
                future = model.make_future_dataframe(periods=30)
                forecast = model.predict(future)

                # Sirf next 30 days
                next_30 = forecast.tail(30)

                predicted = max(0, float(next_30['yhat'].sum()))
                lower = max(0, float(next_30['yhat_lower'].sum()))
                upper = max(0, float(next_30['yhat_upper'].sum()))

                # Trend detect karo
                if len(forecast) > 60:
                    recent = forecast.tail(60)
                    first_half = recent.head(30)['yhat'].mean()
                    second_half = recent.tail(30)['yhat'].mean()

                    if second_half > first_half * 1.05:
                        trend = "increasing"
                    elif second_half < first_half * 0.95:
                        trend = "decreasing"
                    else:
                        trend = "stable"
                else:
                    trend = "stable"

                total += predicted

                predictions.append({
                    "category": cat,
                    "predicted_amount": round(predicted, 2),
                    "lower_bound": round(lower, 2),
                    "upper_bound": round(upper, 2),
                    "trend": trend,
                    "confidence": 0.8,
                    "daily_average": round(predicted / 30, 2),
                })

            except Exception as e:
                print(f"   Prediction error for {cat}: {e}")
                continue

        # Sort by amount (highest first)
        predictions.sort(key=lambda x: x["predicted_amount"], reverse=True)

        # Savings potential calculate karo
        # Agar top 3 categories mein 20% cut karo
        top_3_total = sum(
            p["predicted_amount"] for p in predictions[:3]
        )
        savings_potential = round(top_3_total * 0.20, 2)

        return {
            "predictions": predictions,
            "total_predicted": round(total, 2),
            "forecast_period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            },
            "savings_potential": savings_potential,
            "top_spending_category": (
                predictions[0]["category"] if predictions else None
            ),
            "model_version": self._model_data.get("version", "1.0.0"),
        }

    def predict_category(
        self,
        category: str,
        days: int = 30
    ) -> dict:
        """Single category ka prediction."""
        if not self._model_data:
            return {"error": "Model not loaded"}

        models = self._model_data["models"]

        if category not in models:
            return {
                "error": f"Category '{category}' not in model",
                "available": list(models.keys())
            }

        model = models[category]

        try:
            future = model.make_future_dataframe(periods=days)
            forecast = model.predict(future)
            next_period = forecast.tail(days)

            daily_forecasts = []
            for _, row in next_period.iterrows():
                daily_forecasts.append({
                    "date": row['ds'].strftime("%Y-%m-%d"),
                    "predicted": max(0, round(float(row['yhat']), 2)),
                    "lower": max(0, round(float(row['yhat_lower']), 2)),
                    "upper": max(0, round(float(row['yhat_upper']), 2)),
                })

            total = max(0, float(next_period['yhat'].sum()))

            return {
                "category": category,
                "total_predicted": round(total, 2),
                "daily_forecasts": daily_forecasts,
                "daily_average": round(total / days, 2),
            }

        except Exception as e:
            return {"error": str(e)}

    def get_savings_advice(
        self,
        predicted_expenses: float,
        monthly_income: float = 50000
    ) -> dict:
        """
        50-30-20 rule se savings advice.
        50% needs, 30% wants, 20% savings
        """
        needs_budget = monthly_income * 0.50
        wants_budget = monthly_income * 0.30
        savings_target = monthly_income * 0.20

        actual_savings = monthly_income - predicted_expenses
        savings_rate = (actual_savings / monthly_income * 100
                       if monthly_income > 0 else 0)

        if savings_rate >= 20:
            status = "excellent"
            message = "Bahut achha! Tu 20%+ save kar raha hai. Keep it up! 🎉"
        elif savings_rate >= 10:
            status = "good"
            message = "Achha chal raha hai! Thoda aur cut karke 20% target karo. 💪"
        elif savings_rate >= 0:
            status = "warning"
            message = "Savings kam hai. Kuch expenses reduce karo. ⚠️"
        else:
            status = "danger"
            message = "Tum overspending kar rahe ho! Turant budget banao. 🚨"

        return {
            "monthly_income": monthly_income,
            "predicted_expenses": round(predicted_expenses, 2),
            "predicted_savings": round(actual_savings, 2),
            "savings_rate": round(savings_rate, 1),
            "status": status,
            "message": message,
            "targets": {
                "needs_budget": needs_budget,
                "wants_budget": wants_budget,
                "savings_target": savings_target,
            }
        }

    def _fallback_prediction(self) -> dict:
        """Model load nahi hua toh fallback."""
        return {
            "predictions": [],
            "total_predicted": 0,
            "error": "Prediction model not loaded. Run: python ml/spending_predictor.py",
        }

    @property
    def is_loaded(self) -> bool:
        return self._model_data is not None

# Global instance
predictor = PredictionService()