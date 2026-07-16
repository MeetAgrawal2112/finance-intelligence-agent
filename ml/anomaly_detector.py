import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timezone
from collections import defaultdict

def generate_normal_transactions(n=500):
    np.random.seed(42)
    transactions = []

    categories = {
        'Groceries':     {'mean': 1500,  'std': 500,   'freq': 7},
        'Dining Out':    {'mean': 500,   'std': 200,   'freq': 2},
        'Transport':     {'mean': 200,   'std': 100,   'freq': 1},
        'Shopping':      {'mean': 2000,  'std': 1000,  'freq': 14},
        'Entertainment': {'mean': 800,   'std': 300,   'freq': 10},
        'Utilities':     {'mean': 2000,  'std': 500,   'freq': 30},
        'Healthcare':    {'mean': 1000,  'std': 500,   'freq': 30},
        'Subscriptions': {'mean': 500,   'std': 100,   'freq': 30},
    }

    for _ in range(n):
        cat = np.random.choice(list(categories.keys()))
        params = categories[cat]

        amount = max(50, np.random.normal(params['mean'], params['std']))
        probs = np.array([1,2,3,4,4,4,4,3,3,3,3,2,2,2,1], dtype=float)
        probs = probs / probs.sum()  # Exactly 1.0 guarantee
        hour = np.random.choice(range(8, 23), p=probs)
        transactions.append({
            'amount': round(amount, 2),
            'hour': hour,
            'day_of_week': np.random.randint(0, 7),
            'category': cat,
            'is_anomaly': 0
        })

    return transactions

def extract_features(transactions: list) -> np.ndarray:
    features = []
    for t in transactions:
        amount = t['amount']
        hour = t.get('hour', 12)
        dow = t.get('day_of_week', 0)

        features.append([
            amount,
            np.log1p(amount),           # log transform
            hour,
            dow,
            1 if dow >= 5 else 0,       # is_weekend
            1 if hour >= 23 or hour <= 5 else 0,  # is_night
        ])

    return np.array(features)

# ─── Train Model ──────────────────────────────────────────────────────────────

print("=" * 60)
print("  ANOMALY DETECTION MODEL TRAINING")
print("=" * 60)

# Training data generate karo
print("\n📊 Generating training data...")
normal_txns = generate_normal_transactions(500)
print(f"   Normal transactions: {len(normal_txns)}")

X = extract_features(normal_txns)
print(f"   Features per transaction: {X.shape[1]}")
print(f"   Feature names: amount, log_amount, hour, day_of_week, is_weekend, is_night")

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Isolation Forest train karo
print("\n🏋️  Training Isolation Forest...")
iso_forest = IsolationForest(
    n_estimators=200,      # zyada trees = better accuracy
    contamination=0.05,    # 5% anomalies expected
    random_state=42,
    max_samples='auto'
)
iso_forest.fit(X_scaled)
print("   Training complete!")

# ─── Test with Anomalies ──────────────────────────────────────────────────────

print("\n🧪 Testing with known anomalies:")
print("-" * 50)

test_cases = [
    # Normal transactions
    {"desc": "Normal grocery ₹1500",
     "amount": 1500, "hour": 10, "day_of_week": 2, "expected": "NORMAL"},
    {"desc": "Normal dining ₹400",
     "amount": 400,  "hour": 13, "day_of_week": 1, "expected": "NORMAL"},
    {"desc": "Normal transport ₹200",
     "amount": 200,  "hour": 9,  "day_of_week": 0, "expected": "NORMAL"},

    # Anomalies
    {"desc": "HUGE amount ₹95,000 midnight",
     "amount": 95000, "hour": 2, "day_of_week": 3, "expected": "ANOMALY"},
    {"desc": "Large shopping ₹50,000",
     "amount": 50000, "hour": 15, "day_of_week": 0, "expected": "ANOMALY"},
    {"desc": "Odd hour transaction 3AM ₹8000",
     "amount": 8000, "hour": 3, "day_of_week": 2, "expected": "ANOMALY"},
    {"desc": "Very large dining ₹25,000",
     "amount": 25000, "hour": 20, "day_of_week": 6, "expected": "ANOMALY"},
]

for tc in test_cases:
    features = extract_features([tc])
    features_scaled = scaler.transform(features)

    # Isolation Forest score (-1=anomaly, 1=normal)
    prediction = iso_forest.predict(features_scaled)[0]
    score = iso_forest.score_samples(features_scaled)[0]

    # Normalize score to 0-1 (higher = more anomalous)
    anomaly_score = max(0, min(1, (-score - 0.3) / 0.7))

    status = "🚨 ANOMALY" if prediction == -1 else "✅ NORMAL"
    match = "✓" if (
        (tc["expected"] == "ANOMALY" and prediction == -1) or
        (tc["expected"] == "NORMAL" and prediction == 1)
    ) else "✗"

    print(f"   {match} {status} | Score: {anomaly_score:.2f} | {tc['desc']}")



os.makedirs("ml/models", exist_ok=True)

model_data = {
    "iso_forest": iso_forest,
    "scaler": scaler,
    "version": "1.0.0",
    "feature_names": [
        "amount", "log_amount", "hour",
        "day_of_week", "is_weekend", "is_night"
    ],
    "contamination": 0.05,
    "anomaly_threshold": 0.5,
}

model_path = "ml/models/anomaly_detector.pkl"
joblib.dump(model_data, model_path)

size = os.path.getsize(model_path) / 1024
print(f"\n✅ Model saved: {model_path}")
print(f"   File size: {size:.1f} KB")
print("\n" + "=" * 60)
print("  TRAINING COMPLETE! 🎉")
print("=" * 60)