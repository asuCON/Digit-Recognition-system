#!/usr/bin/env python
"""
Run neural system tests - no pytest required.
Execute: python run_neural_test.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    errors = []
    print("=" * 50)
    print("MNIST Neural System Test Suite")
    print("=" * 50)

    # Test 1: Load data
    print("\n[1] Testing MNIST data load...")
    try:
        from model import load_mnist_data
        (x_train, y_train), (x_test, y_test) = load_mnist_data()
        assert x_train.shape == (60000, 28, 28, 1), f"Bad shape: {x_train.shape}"
        assert x_test.shape == (10000, 28, 28, 1), f"Bad shape: {x_test.shape}"
        print("    OK")
    except Exception as e:
        errors.append(f"Data load: {e}")
        print(f"    FAIL: {e}")

    # Test 2: Preprocessing
    print("\n[2] Testing preprocessing...")
    try:
        import numpy as np
        from preprocessing import preprocess
        arr = np.random.randint(0, 256, (28, 28), dtype=np.uint8)
        out = preprocess(arr)
        assert out.shape == (28, 28), f"Bad shape: {out.shape}"
        assert 0 <= out.min() <= out.max() <= 1, "Values out of range"
        print("    OK")
    except Exception as e:
        errors.append(f"Preprocessing: {e}")
        print(f"    FAIL: {e}")

    # Test 3: Build advanced CNN
    print("\n[3] Testing advanced CNN build...")
    try:
        from model import build_cnn_model, load_mnist_data
        model = build_cnn_model()
        assert model.input_shape == (None, 28, 28, 1), f"Bad input: {model.input_shape}"
        assert model.output_shape == (None, 10), f"Bad output: {model.output_shape}"
        (_, _), (x_test, _) = load_mnist_data()
        pred = model.predict(x_test[:2], verbose=0)
        assert pred.shape == (2, 10), f"Bad pred shape: {pred.shape}"
        assert abs(pred.sum(axis=1) - 1).max() < 1e-5, "Probs don't sum to 1"
        print("    OK")
    except Exception as e:
        errors.append(f"Advanced CNN: {e}")
        print(f"    FAIL: {e}")

    # Test 4: Forward pass & prediction
    print("\n[4] Testing predict_digit...")
    try:
        from model import build_simple_model, load_mnist_data, predict_digit
        import numpy as np
        model = build_simple_model()
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
        (_, _), (x_test, y_test) = load_mnist_data()
        # Quick fit on subset
        y_cat = np.eye(10)[np.argmax(y_test[:500], axis=1)]
        model.fit(x_test[:500], y_cat, epochs=1, verbose=0)
        probs = predict_digit(model, x_test[0])
        assert len(probs) == 10, f"Bad probs length: {len(probs)}"
        assert abs(sum(probs) - 1) < 1e-5, f"Probs sum: {sum(probs)}"
        digit = np.argmax(probs)
        assert 0 <= digit <= 9, f"Bad digit: {digit}"
        print(f"    OK (sample prediction: {digit})")
    except Exception as e:
        errors.append(f"predict_digit: {e}")
        print(f"    FAIL: {e}")

    # Test 5: Predictor service
    print("\n[5] Testing DigitPredictor...")
    try:
        from predictor import DigitPredictor
        from model import build_simple_model, load_mnist_data
        import numpy as np
        import tempfile
        model = build_simple_model()
        model.compile(optimizer="adam", loss="categorical_crossentropy")
        (_, _), (x_test, y_test) = load_mnist_data()
        model.fit(x_test[:500], np.eye(10)[np.argmax(y_test[:500], axis=1)], epochs=1, verbose=0)
        with tempfile.NamedTemporaryFile(suffix=".keras", delete=False) as f:
            path = f.name
        try:
            model.save(path)
            predictor = DigitPredictor(model_path=path)
            assert predictor.load(), "Failed to load"
            result = predictor.predict(x_test[0])
            assert result.digit in range(10), f"Bad digit: {result.digit}"
            assert 0 <= result.confidence <= 1, f"Bad confidence: {result.confidence}"
            assert len(result.probabilities) == 10, f"Bad probs: {len(result.probabilities)}"
            print(f"    OK (prediction: {result.digit}, conf: {result.confidence:.2f})")
        finally:
            os.unlink(path)
    except Exception as e:
        errors.append(f"DigitPredictor: {e}")
        print(f"    FAIL: {e}")

    # Summary
    print("\n" + "=" * 50)
    if errors:
        print("RESULT: FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1
    else:
        print("RESULT: ALL TESTS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(run_tests())
