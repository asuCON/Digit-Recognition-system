#!/usr/bin/env python3
"""Evaluate model. Outputs confusion matrix and metrics. Called by PHP."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    try:
        from sklearn.metrics import confusion_matrix, classification_report
        from predictor import get_predictor
        from model import load_mnist_data
        from config import MODEL_PATH

        pred = get_predictor(model_path=MODEL_PATH)
        if not pred.load():
            print(json.dumps({"error": "Model not loaded"}))
            return

        _, (x_test, y_test) = load_mnist_data()
        import numpy as np
        y_pred = pred._model.predict(x_test, verbose=0).argmax(axis=1)
        y_true = np.argmax(y_test, axis=1)

        report = classification_report(y_true, y_pred, output_dict=True)

        print(json.dumps({
            "accuracy": float((y_pred == y_true).mean()),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
            "classification_report": report,
            "precision": report.get("weighted avg", {}).get("precision", "—"),
            "recall": report.get("weighted avg", {}).get("recall", "—"),
            "f1_score": report.get("weighted avg", {}).get("f1-score", "—"),
        }))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
