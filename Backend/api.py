"""
MNIST Digit Recognition - REST API
FastAPI backend compatible with React and Node.js frontends.
"""

import os
import base64
import io
from typing import Optional

import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from PIL import Image

from config import CORS_ORIGINS, MODEL_PATH
from model import (
    load_mnist_data,
    build_cnn_model,
    build_simple_model,
    train_model,
)
from predictor import get_predictor, PredictionResult

# --- App ---

app = FastAPI(
    title="MNIST Digit Recognition API",
    description="Neural network API for digit recognition - React & Node.js compatible",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Schemas ---

class PredictBase64Request(BaseModel):
    image: str


class PredictResponse(BaseModel):
    digit: int
    confidence: float
    probabilities: list[float]
    label: str


class TrainRequest(BaseModel):
    model_type: str = "advanced"
    epochs: int = 15
    batch_size: int = 128


class TrainResponse(BaseModel):
    message: str
    test_accuracy: float
    test_loss: float


class ModelStatusResponse(BaseModel):
    loaded: bool
    path: str


class ApiConfigResponse(BaseModel):
    baseUrl: str
    endpoints: dict
    corsAllowed: list[str]


# --- Endpoints ---

def _pred_to_response(r: PredictionResult) -> PredictResponse:
    return PredictResponse(
        digit=r.digit,
        confidence=r.confidence,
        probabilities=r.probabilities,
        label=r.label,
    )


@app.get("/")
def root():
    """API info and health check."""
    return {
        "name": "MNIST Digit Recognition API",
        "status": "running",
        "version": "2.0.0",
        "endpoints": {
            "predict": "POST /predict | POST /predict/base64",
            "train": "POST /train",
            "status": "GET /model/status",
            "config": "GET /config",
            "samples": "GET /samples",
            "evaluate": "GET /evaluate",
        },
    }


@app.get("/config", response_model=ApiConfigResponse)
def api_config():
    """React/frontend config - base URL and endpoint list."""
    # In browser, use relative or env-based URL
    return ApiConfigResponse(
        baseUrl="/api",  # or process.env.REACT_APP_API_URL
        endpoints={
            "predict": "/predict",
            "predictBase64": "/predict/base64",
            "train": "/train",
            "status": "/model/status",
            "samples": "/samples",
            "evaluate": "/evaluate",
        },
        corsAllowed=CORS_ORIGINS,
    )


@app.get("/health")
def health():
    """Health check for load balancers and React checks."""
    predictor = get_predictor()
    return {
        "status": "ok",
        "model_loaded": predictor.load(),
    }


@app.get("/model/status", response_model=ModelStatusResponse)
def model_status():
    predictor = get_predictor()
    loaded = predictor.load()
    return ModelStatusResponse(loaded=loaded, path=MODEL_PATH)


@app.post("/predict", response_model=PredictResponse)
async def predict_from_file(file: UploadFile = File(...)):
    """Predict from uploaded image (PNG, JPEG)."""
    predictor = get_predictor()
    if not predictor.load():
        raise HTTPException(503, "Model not loaded. Train via POST /train")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image (PNG, JPEG)")

    contents = await file.read()
    try:
        result = predictor.predict(contents)
    except Exception as e:
        raise HTTPException(400, f"Invalid image: {str(e)}")

    return _pred_to_response(result)


@app.post("/predict/base64", response_model=PredictResponse)
async def predict_from_base64(body: PredictBase64Request):
    """Predict from base64 image (e.g. canvas.toDataURL('image/png'))."""
    predictor = get_predictor()
    if not predictor.load():
        raise HTTPException(503, "Model not loaded. Train via POST /train")

    try:
        result = predictor.predict(body.image)
    except Exception as e:
        raise HTTPException(400, f"Invalid base64 image: {str(e)}")

    return _pred_to_response(result)


@app.post("/train", response_model=TrainResponse)
async def train(body: TrainRequest):
    """Train a new model."""
    predictor = get_predictor()

    (x_train, y_train), (x_test, y_test) = load_mnist_data()

    if body.model_type.lower() == "simple":
        model = build_simple_model()
    else:
        model = build_cnn_model()

    history, test_loss, test_acc = train_model(
        model, x_train, y_train, x_test, y_test,
        epochs=body.epochs,
        batch_size=body.batch_size,
    )

    model.save(MODEL_PATH)
    predictor.set_model(model)

    return TrainResponse(
        message="Training complete",
        test_accuracy=float(test_acc),
        test_loss=float(test_loss),
    )


@app.get("/samples")
async def get_samples(count: int = 10, digit: Optional[int] = None):
    """Get MNIST samples as base64 for gallery."""
    (x_train, y_train), _ = load_mnist_data()
    y_labels = np.argmax(y_train, axis=1)

    if digit is not None:
        indices = np.where(y_labels == digit)[0]
    else:
        indices = np.arange(len(x_train))

    indices = np.random.choice(indices, min(count, len(indices)), replace=False)
    samples = []

    for idx in indices:
        img = (x_train[idx].squeeze() * 255).astype(np.uint8)
        pil = Image.fromarray(img, mode="L")
        buf = io.BytesIO()
        pil.save(buf, format="PNG")
        samples.append({
            "image_base64": base64.b64encode(buf.getvalue()).decode(),
            "label": int(y_labels[idx]),
        })

    return {"samples": samples}


@app.get("/evaluate")
async def evaluate():
    """Model evaluation metrics."""
    from sklearn.metrics import confusion_matrix, classification_report

    predictor = get_predictor()
    if not predictor.load():
        raise HTTPException(503, "Model not loaded")

    _, (x_test, y_test) = load_mnist_data()
    model = predictor._model
    y_pred = np.argmax(model.predict(x_test, verbose=0), axis=1)
    y_true = np.argmax(y_test, axis=1)

    return {
        "accuracy": float(np.mean(y_pred == y_true)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, output_dict=True),
    }


if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)
