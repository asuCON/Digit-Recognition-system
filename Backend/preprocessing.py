"""
Image preprocessing pipeline for MNIST digit recognition.
Handles various input formats (PIL, numpy, base64) and normalizes for the neural network.
"""

import base64
import io
from typing import Union

import numpy as np
from PIL import Image


def to_grayscale(img: Union[np.ndarray, Image.Image]) -> np.ndarray:
    """Convert to grayscale 2D array (values 0..255)."""
    if isinstance(img, Image.Image):
        return np.array(img.convert("L"))
    arr = np.array(img)
    if arr.ndim == 3:
        # Drop alpha if present
        if arr.shape[-1] == 4:
            arr = arr[:, :, :3]
        # Simple RGB->gray average
        arr = np.mean(arr, axis=-1)
    return arr.astype(np.float32)


def _crop_and_center_to_28x28(arr: np.ndarray) -> np.ndarray:
    """
    Crop around the digit, center it, and resize to 28x28.

    This is critical when going from a large drawing canvas to MNIST format,
    so that the digit isn't tiny or off-center.
    """
    # Ensure we are working with 0..255 grayscale
    if arr.max() <= 1.0:
        arr_255 = (arr * 255.0).astype(np.uint8)
    else:
        arr_255 = arr.astype(np.uint8)

    h, w = arr_255.shape

    # Estimate background from image border and invert if background is light.
    border_pixels = np.concatenate(
        [arr_255[0, :], arr_255[-1, :], arr_255[:, 0], arr_255[:, -1]]
    )
    bg = float(np.median(border_pixels)) / 255.0
    if bg > 0.5:
        # Light background, dark digit -> invert so digit is bright on dark.
        arr_255 = 255 - arr_255

    # Normalize to [0, 1] for thresholding and later use
    arr_norm = arr_255.astype(np.float32) / 255.0

    # Find "ink" pixels (digit) by simple threshold
    mask = arr_norm > 0.2
    if not np.any(mask):
        # Nothing drawn; return a blank MNIST-style image
        return np.zeros((28, 28), dtype=np.float32)

    # Bounding box of the digit
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    cropped = arr_norm[rmin : rmax + 1, cmin : cmax + 1]

    # Pad to square to preserve aspect ratio when resizing
    ch, cw = cropped.shape
    size = max(ch, cw)
    padded = np.zeros((size, size), dtype=np.float32)
    y_off = (size - ch) // 2
    x_off = (size - cw) // 2
    padded[y_off : y_off + ch, x_off : x_off + cw] = cropped

    # Resize to 28x28 using PIL
    pil = Image.fromarray((padded * 255.0).astype(np.uint8), mode="L")
    pil = pil.resize((28, 28), Image.Resampling.LANCZOS)
    out = np.array(pil).astype(np.float32) / 255.0
    return out


def preprocess(image: Union[np.ndarray, Image.Image, bytes, str]) -> np.ndarray:
    """
    Full preprocessing pipeline. Output: (28, 28) float32 in [0, 1], ready for model.
    
    Accepts:
    - numpy array (H, W) or (H, W, C)
    - PIL Image
    - raw bytes (PNG/JPEG)
    - base64 string (with or without data URL prefix)
    """
    if isinstance(image, str):
        if image.strip().startswith("data:"):
            image = image.split(",", 1)[-1]
        image = base64.b64decode(image)
    if isinstance(image, bytes):
        image = Image.open(io.BytesIO(image)).convert("L")
        image = np.array(image)

    gray = to_grayscale(image)

    # If this already looks like a MNIST-sized image, just normalize.
    if gray.shape == (28, 28):
        arr = gray.astype(np.float32)
        if arr.max() > 1.0:
            arr = arr / 255.0
        return arr.astype(np.float32)

    # For larger inputs (e.g. canvas), crop, center, and resize to 28x28.
    normalized = _crop_and_center_to_28x28(gray)
    return normalized.astype(np.float32)
