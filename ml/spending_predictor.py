import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta, timezone
from ml.forecaster import SimpleForecaster  # Only import, no class here

def generate_data(months=6):
    np.random.seed(42)
    cats = {
        'Groceries':     {'base': 4000, 'std': 500,  'trend': 50},
        'Dining Out':    {'base': 3000, 'std': 800,  'trend': 100},
        'Transport':     {'base': 2000, 'std': 300,  'trend': 20},
        'Shopping':      {'base': 5000, 'std': 2000, 'trend': 200},
        'Entertainment': {'base': 1500, 'std': 400,  'trend': 50},
        'Utilities':     {'base': 3000, 'std': 200,  'trend': 0},
        'Healthcare':    {'base': 1000, 'std': 500,  'trend': 30},
        'Subscriptions': {'base': 800,  'std': 50,   'trend': 0},
    }
    records = []
    start = datetime.now() - timedelta(days=months*30)
    for i in range(months*30):
        date = start + timedelta(days=i)
        mn = i // 30
        for cat, p in cats.items():
            for _ in range(np.random.poisson(2)):
                amt = max(50, np.random.normal(
                    p['base']/20 + p['trend']*mn/20, p['std']/10))
                records.append({'date': date.strftime('%Y-%m-%d'),
                                'amount': round(amt,2), 'category': cat})
    return pd.DataFrame(records)

print("=" * 50)
print("  SPENDING PREDICTION MODEL TRAINING")
print("=" * 50)

df = generate_data(6)
print(f"Transactions: {len(df)}")

forecaster = SimpleForecaster()
forecaster.fit(df)

predictions = forecaster.predict_all()
total = sum(p['predicted_amount'] for p in predictions)
print("\n30-Day Forecast:")
for p in predictions:
    print(f"  {p['category']:<20} Rs.{p['predicted_amount']:>8,.0f}")
print(f"  {'TOTAL':<20} Rs.{total:>8,.0f}")

os.makedirs("ml/models", exist_ok=True)
joblib.dump({
    "forecaster": forecaster,
    "categories": list(forecaster.models.keys()),
    "version": "1.0.0",
    "trained_at": datetime.now(timezone.utc).isoformat(),
}, "ml/models/spending_predictor.pkl")
print("\n✅ Model saved!")
