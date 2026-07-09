# ml/train_categoriser.py
"""
Expense Categorisation Model Training Script.

Run: python ml/train_categoriser.py
Output: ml/models/categoriser.pkl
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score
)
import re
from ml.data.transactions_dataset import TRAINING_DATA, CATEGORIES
from ml.text_utils import clean_text

# ─── Prepare Data ─────────────────────────────────────────────────────────────

print("=" * 60)
print("  EXPENSE CATEGORISATION MODEL TRAINING")
print("=" * 60)

# Data split karo
descriptions = [clean_text(desc) for desc, _ in TRAINING_DATA]
labels = [label for _, label in TRAINING_DATA]

print(f"\n📊 Dataset Info:")
print(f"   Total samples: {len(descriptions)}")
print(f"   Categories: {len(set(labels))}")
print(f"   Category distribution:")
from collections import Counter
counts = Counter(labels)
for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
    bar = "█" * count
    print(f"   {cat:<20} {count:3d} {bar}")

# Train/test split — 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    descriptions, labels,
    test_size=0.2,
    random_state=42,
    stratify=labels  # Har category same proportion mein ho
)

print(f"\n   Training samples: {len(X_train)}")
print(f"   Testing samples:  {len(X_test)}")

# ─── Model Pipeline ───────────────────────────────────────────────────────────

"""
Pipeline kya karta hai:
Step 1: TfidfVectorizer
  - Text → numeric matrix
  - ngram_range=(1,2): single words + word pairs
    "Zomato" aur "Zomato food" dono features bante hain
  - max_features=5000: top 5000 important features rakh
  - sublinear_tf=True: frequency ko log scale pe rakh
    (1 baar vs 10 baar ka difference smooth karta hai)

Step 2: LogisticRegression
  - Multi-class classification
  - C=10: regularization — overfitting rok
  - max_iter=1000: convergence ke liye
"""

model = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 3),       # trigrams bhi add karo
        max_features=10000,        # zyada features
        sublinear_tf=True,
        min_df=1,
        analyzer='word',
        token_pattern=r'\b[a-z][a-z]+\b',
        strip_accents='unicode',
    )),
    ('clf', LogisticRegression(
        C=50,                      # zyada flexibility
        max_iter=2000,
        random_state=42,
        solver='lbfgs',
        class_weight='balanced'    # imbalanced classes handle karo
    ))
])


# ─── Training ─────────────────────────────────────────────────────────────────

print("\n🏋️  Training model...")
model.fit(X_train, y_train)
print("   Training complete!")

# ─── Evaluation ───────────────────────────────────────────────────────────────

print("\n📈 Model Evaluation:")

# Test accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\n   Test Accuracy: {accuracy:.1%}")

# Cross validation — 5 folds
print("\n   Cross-Validation (5-fold):")
cv_scores = cross_val_score(model, descriptions, labels, cv=5, scoring='accuracy')
print(f"   Scores: {[f'{s:.1%}' for s in cv_scores]}")
print(f"   Mean:   {cv_scores.mean():.1%} ± {cv_scores.std():.1%}")

# Detailed report
print("\n   Classification Report:")
print(classification_report(y_test, y_pred, target_names=sorted(set(labels))))

# ─── Manual Tests ─────────────────────────────────────────────────────────────

print("\n🧪 Manual Prediction Tests:")
print("-" * 50)

test_cases = [
    "Zomato food order delivered",
    "BigBasket weekly grocery",
    "House rent payment March",
    "Uber ride home office",
    "Amazon shopping sale",
    "Netflix subscription renewal",
    "Apollo pharmacy medicine",
    "MSEB electricity bill",
    "GitHub Pro monthly",
    "Udemy Python course",
    "MakeMyTrip Goa trip",
    "Salary credit March",
    "Upwork client payment",
    "Zerodha SIP investment",
    "ATM cash withdrawal",
    "Swiggy biryani order",
    "Petrol fill HP pump",
    "PVR cinema ticket",
    "Doctor consultation fee",
    "Jio recharge 599 plan",
]

for desc in test_cases:
    cleaned = clean_text(desc)
    prediction = model.predict([cleaned])[0]
    probabilities = model.predict_proba([cleaned])[0]
    confidence = max(probabilities)

    # Confidence ke hisaab se emoji
    emoji = "✅" if confidence > 0.8 else "⚠️" if confidence > 0.5 else "❓"

    print(f"   {emoji} \"{desc}\"")
    print(f"      → {prediction} ({confidence:.0%} confident)")

# ─── Save Model ───────────────────────────────────────────────────────────────

os.makedirs("ml/models", exist_ok=True)

# Model + metadata save karo
model_data = {
    "model": model,
    "categories": CATEGORIES,
    "version": "1.0.0",
    "clean_text_fn": clean_text,
    "training_samples": len(descriptions),
    "accuracy": float(accuracy),
    "cv_mean": float(cv_scores.mean()),
}

model_path = "ml/models/categoriser.pkl"
joblib.dump(model_data, model_path)

file_size = os.path.getsize(model_path) / 1024
print(f"\n✅ Model saved: {model_path}")
print(f"   File size: {file_size:.1f} KB")
print(f"   Version: 1.0.0")
print(f"   Accuracy: {accuracy:.1%}")
print(f"   CV Mean: {cv_scores.mean():.1%}")
print("\n" + "=" * 60)
print("  TRAINING COMPLETE! 🎉")
print("=" * 60)