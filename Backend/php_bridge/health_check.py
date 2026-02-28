#!/usr/bin/env python3
"""Health check - returns model loaded status. Called by PHP."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MODEL_PATH

def main():
    try:
        from predictor import get_predictor
        pred = get_predictor(model_path=MODEL_PATH)
        loaded = pred.load()
        print(json.dumps({"loaded": loaded, "path": MODEL_PATH}))
    except Exception as e:
        print(json.dumps({"loaded": False, "path": MODEL_PATH, "error": str(e)}))

if __name__ == "__main__":
    main()
