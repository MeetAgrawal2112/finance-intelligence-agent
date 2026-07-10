# ml/forecaster.py
import numpy as np
from sklearn.linear_model import LinearRegression

class SimpleForecaster:
    def __init__(self):
        self.models = {}

    def fit(self, df):
        import pandas as pd
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        for cat in df['category'].unique():
            cat_data = df[df['category'] == cat]
            monthly = cat_data.groupby('month')['amount'].sum()
            if len(monthly) < 2:
                continue
            values = monthly.values
            idx = np.arange(len(values)).reshape(-1, 1)
            reg = LinearRegression().fit(idx, values)
            residuals = values - reg.predict(idx)
            self.models[cat] = {
                'regression': reg,
                'n_months': len(values),
                'ma3': float(np.mean(values[-3:])),
                'std': float(np.std(residuals)),
                'slope': float(reg.coef_[0]),
            }
        return self

    def predict_next_month(self, category):
        if category not in self.models:
            return None
        m = self.models[category]
        trend_pred = float(m['regression'].predict([[m['n_months']]])[0])
        predicted = max(0, 0.6 * trend_pred + 0.4 * m['ma3'])
        lower = max(0, predicted - 1.5 * m['std'])
        upper = predicted + 1.5 * m['std']
        slope = m['slope']
        trend = "increasing" if slope > 50 else "decreasing" if slope < -50 else "stable"
        return {
            "category": category,
            "predicted_amount": round(predicted, 2),
            "lower_bound": round(lower, 2),
            "upper_bound": round(upper, 2),
            "trend": trend,
            "confidence": 0.75,
            "daily_average": round(predicted / 30, 2),
        }

    def predict_all(self):
        results = [self.predict_next_month(c) for c in self.models]
        results = [r for r in results if r]
        return sorted(results, key=lambda x: -x['predicted_amount'])
