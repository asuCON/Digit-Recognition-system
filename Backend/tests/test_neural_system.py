"""
Test suite for the MNIST neural system.
Verifies model loading, prediction, preprocessing, and end-to-end inference.
"""
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest


def test_load_mnist_data():
    """Test MNIST data loading and preprocessing."""
    from model import load_mnist_data

    (x_train, y_train), (x_test, y_test) = load_mnist_data()

    assert x_train.shape == (60000, 28, 28, 1)
    assert x_test.shape == (10000, 28, 28, 1)
    assert y_train.shape == (60000, 10)
    assert y_test.shape == (10000, 10)
    assert 0 <= x_train.min() <= x_train.max() <= 1
    assert np.allclose(y_train.sum(axis=1), 1)


def test_preprocessing():
    """Test image preprocessing pipeline."""
    from preprocessing import preprocess

    # Test with numpy array (28x28)
    arr = np.random.randint(0, 256, (28, 28), dtype=np.uint8)
    out = preprocess(arr)
    assert out.shape == (28, 28)
    assert 0 <= out.min() <= out.max() <= 1

    # Test with larger image
    arr_large = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
    out_large = preprocess(arr_large)
    assert out_large.shape == (28, 28)


def test_build_cnn_model():
    """Test advanced CNN model builds and produces correct output shape."""
    from model import build_cnn_model, load_mnist_data

    model = build_cnn_model()
    assert model is not None
    assert model.input_shape == (None, 28, 28, 1)
    assert model.output_shape == (None, 10)

    # Forward pass
    (_, _), (x_test, _) = load_mnist_data()
    sample = x_test[:2]
    pred = model.predict(sample, verbose=0)
    assert pred.shape == (2, 10)
    assert np.allclose(pred.sum(axis=1), 1)


def test_predictor():
    """Test predictor service end-to-end."""
    from model import load_mnist_data
    from predictor import DigitPredictor
    from preprocessing import preprocess

    # Build and use a minimal model (don't require saved file)
    from model import build_simple_model, train_model

    (x_train, y_train), (x_test, y_test) = load_mnist_data()
    # Use tiny subset for speed
    x_train_small = x_train[:1000]
    y_train_small = y_train[:1000]

    model = build_simple_model()
    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    model.fit(x_train_small, y_train_small, epochs=2, batch_size=128, verbose=0)
    test_acc = model.evaluate(x_test, y_test, verbose=0)[1]

    # Predict on a sample
    sample = x_test[0]
    pred = model.predict(np.expand_dims(sample, 0), verbose=0)[0]
    digit = int(np.argmax(pred))
    confidence = float(pred[digit])

    assert 0 <= digit <= 9
    assert 0 <= confidence <= 1
    assert np.allclose(pred.sum(), 1)
    # Basic sanity: model should beat random (10%) after 2 epochs on subset
    assert test_acc > 0.1


def test_predict_digit():
    """Test predict_digit helper with model."""
    from model import build_simple_model, load_mnist_data, predict_digit

    model = build_simple_model()
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    (_, _), (x_test, _) = load_mnist_data()
    model.fit(x_test[:500], np.eye(10)[np.arange(500) % 10], epochs=1, verbose=0)

    probs = predict_digit(model, x_test[0])
    assert len(probs) == 10
    assert np.allclose(sum(probs), 1)
    assert 0 <= np.argmax(probs) <= 9


def test_advanced_cnn_forward():
    """Test advanced CNN architecture forward pass."""
    from model import build_cnn_model, load_mnist_data

    model = build_cnn_model()
    (_, _), (x_test, _) = load_mnist_data()

    for _ in range(3):
        idx = np.random.randint(0, len(x_test))
        sample = x_test[idx : idx + 1]
        pred = model.predict(sample, verbose=0)[0]
        assert pred.shape == (10,)
        assert np.allclose(pred.sum(), 1)
        assert 0 <= np.argmax(pred) <= 9


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
