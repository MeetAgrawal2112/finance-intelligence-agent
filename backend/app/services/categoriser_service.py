# app/services/categoriser_service.py
"""
ML Categorisation Service.
FastAPI startup pe model load hoga,
phir har transaction prediction ke liye yahi use hoga.
"""

import joblib
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from ml.text_utils import clean_text
import re
from typing import Optional

class CategoriserService:
    """
    Singleton pattern — model ek baar load hota hai
    aur poori app mein same instance use hoti hai.
    Kyun? Model load karna slow aur memory-intensive hai.
    """
    _instance = None
    _model_data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self):
        """
        Model file se load karo.
        FastAPI startup event pe call hoga.
        """
        # Root se relative path
        model_path = os.path.join(
            os.path.dirname(__file__),
            "../../../ml/models/categoriser.pkl"
        )
        model_path = os.path.abspath(model_path)

        if not os.path.exists(model_path):
            print(f"⚠️  Categoriser model not found: {model_path}")
            print("   Run: python ml/train_categoriser.py")
            return False

        try:
            self._model_data = joblib.load(model_path)
            accuracy = self._model_data.get('accuracy', 0)
            print(f"✅ Categoriser loaded — accuracy: {accuracy:.1%}")
            return True
        except Exception as e:
            print(f"❌ Failed to load categoriser: {e}")
            return False


    def predict(self, description: str) -> dict:
        if not self._model_data:
            return {"category": "Other", "confidence": 0.0, "all_probabilities": {}}

        model = self._model_data["model"]
        cleaned = clean_text(description)   # ← self._clean_text की जगह
        
        prediction = model.predict([cleaned])[0]
        probabilities = model.predict_proba([cleaned])[0]
        confidence = float(max(probabilities))
        
        all_probs = {
            cat: float(prob)
            for cat, prob in zip(model.classes_, probabilities)
        }
        
        return {
            "category": prediction,
            "confidence": confidence,
            "all_probabilities": dict(
                sorted(all_probs.items(), key=lambda x: -x[1])[:5]
            )
        }

    def predict_batch(self, descriptions: list[str]) -> list[dict]:
        """Multiple transactions ek saath predict karo."""
        return [self.predict(desc) for desc in descriptions]

    @property
    def is_loaded(self) -> bool:
        return self._model_data is not None

    @property
    def model_info(self) -> dict:
        if not self._model_data:
            return {"loaded": False}
        return {
            "loaded": True,
            "version": self._model_data.get("version"),
            "accuracy": self._model_data.get("accuracy"),
            "training_samples": self._model_data.get("training_samples"),
            "categories": self._model_data.get("categories"),
        }

# Global instance
categoriser = CategoriserService()