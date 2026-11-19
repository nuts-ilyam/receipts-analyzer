from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline


class ProductClassifier:
    def __init__(self, model_path: str | Path, min_confidence: float = 0.5):
        self.model_path = Path(model_path)
        self.min_confidence = min_confidence

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model's file is not found: {self.model_path}")

        self.model: Pipeline = joblib.load(self.model_path)

    def predict_category(
            self, product_name: str
    ) -> tuple[str | None, float]:
        """Receives string with product name, Predict more relevant category with confidence."""

        # Оборачиваем строку в список [product_name], получаем матрицу 1xN и берем 0-ю строку
        probs = self.model.predict_proba([product_name])[0]

        best_idx = int(probs.argmax())
        confidence = float(probs[best_idx])
        category = str(self.model.classes_[best_idx])

        if confidence < self.min_confidence:
            return None, confidence

        return category, confidence

