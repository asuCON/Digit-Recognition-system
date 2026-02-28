"""
Configuration for MNIST Digit Recognition system.
"""

import os
from typing import List

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS - React dev servers (Vite: 5173, CRA: 3000)
CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Add custom origin from env (e.g. production frontend)
_extra = os.getenv("CORS_ORIGINS", "")
if _extra:
    CORS_ORIGINS.extend(x.strip() for x in _extra.split(",") if x.strip())

# Model
MODEL_PATH = os.getenv("MODEL_PATH", "mnist_cnn_model.keras")
MODEL_INPUT_SHAPE = (28, 28, 1)
NUM_CLASSES = 10
