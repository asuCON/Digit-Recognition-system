"""
Prediction service for MNIST digit recognition.
Orchestrates preprocessing, model loading, and inference.
"""

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from config import MODEL_PATH, NUM_CLASSES
from preprocessing import preprocess


@dataclass
class PredictionResult:
    """Structured prediction output."""
    digit: int
    confidence: float
    probabilities: List[float]
    label: str  # "0", "1", ... "9"


class DigitPredictor:
    """Unified prediction interface for the neural network system."""

    def __init__(self, model_path: Optional[str] = None):
        self._model = None
        self._model_path = model_path or MODEL_PATH

    def load(self) -> bool:
        """Load model from disk. Returns True if loaded, False otherwise."""
        import os
        import tensorflow.keras as keras

        if self._model is not None:
            return True
        if not os.path.exists(self._model_path):
            return False
        self._model = keras.models.load_model(self._model_path)
        return True

    def is_loaded(self) -> bool:
        return self._model is not None

    def predict(self, image, return_probs: bool = True) -> PredictionResult:
        """
        Predict digit from image.
        
        Args:
            image: numpy array, PIL Image, bytes, or base64 string
            return_probs: include full probability distribution
            
        Returns:
            PredictionResult with digit, confidence, probabilities
        """
        if not self.is_loaded() and not self.load():
            raise RuntimeError("Model not loaded. Train or load a model first.")

        arr = preprocess(image)
        # Add batch and channel dims
        if arr.ndim == 2:
            arr = np.expand_dims(np.expand_dims(arr, -1), 0)
        else:
            arr = np.expand_dims(arr, 0)

        probs = self._model.predict(arr, verbose=0)[0]
        digit = int(np.argmax(probs))
        confidence = float(probs[digit])

        return PredictionResult(
            digit=digit,
            confidence=confidence,
            probabilities=[float(p) for p in probs] if return_probs else [],
            label=str(digit),
        )

    def predict_batch(self, images: List) -> List[PredictionResult]:
        """Predict for multiple images."""
        return [self.predict(img) for img in images]

    def set_model(self, model):
        """Update the loaded model (e.g. after training)."""
        self._model = model


# Singleton for API use
_predictor: Optional[DigitPredictor] = None


def get_predictor(model_path: Optional[str] = None) -> DigitPredictor:
    """Get or create the global predictor instance. Optionally override model path."""
    global _predictor
    path = model_path or MODEL_PATH
    if _predictor is None or (model_path and _predictor._model_path != model_path):
        _predictor = DigitPredictor(model_path=path)
    return _predictor
