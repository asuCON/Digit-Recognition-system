#!/usr/bin/env python3
"""Get MNIST samples. Reads JSON from stdin, outputs JSON. Called by PHP."""
import json
import sys
import os
import base64
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    try:
        data = json.load(sys.stdin)
        count = int(data.get("count", 10))
        digit = data.get("digit")

        import numpy as np
        from PIL import Image
        from model import load_mnist_data

        (x_train, y_train), _ = load_mnist_data()
        y_labels = np.argmax(y_train, axis=1)

        if digit is not None:
            indices = np.where(y_labels == int(digit))[0]
        else:
            indices = np.arange(len(x_train))

        indices = np.random.choice(indices, min(count, len(indices)), replace=False)
        samples = []
        for idx in indices:
            img = (x_train[idx].squeeze() * 255).astype("uint8")
            pil = Image.fromarray(img, mode="L")
            buf = io.BytesIO()
            pil.save(buf, format="PNG")
            samples.append({
                "image_base64": base64.b64encode(buf.getvalue()).decode(),
                "label": int(y_labels[idx]),
            })

        print(json.dumps({"samples": samples}))
    except Exception as e:
        print(json.dumps({"samples": [], "error": str(e)}))

if __name__ == "__main__":
    main()
