#!/usr/bin/env python3
"""Predict from base64 image. Reads JSON from stdin, outputs JSON. Called by PHP."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    try:
        data = json.load(sys.stdin)
        image_b64 = data.get("image", "")
        if not image_b64:
            print(json.dumps({"error": "Missing image"}))
            return

        from predictor import get_predictor
        from config import MODEL_PATH

        pred = get_predictor(model_path=MODEL_PATH)
        if not pred.load():
            print(json.dumps({"error": "Model not loaded"}))
            return

        result = pred.predict(image_b64)
        print(json.dumps({
            "digit": result.digit,
            "confidence": result.confidence,
            "probabilities": result.probabilities,
            "label": result.label,
        }))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
