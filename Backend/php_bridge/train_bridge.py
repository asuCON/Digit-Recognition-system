#!/usr/bin/env python3
"""Train model. Reads JSON from stdin, outputs JSON. Called by PHP.
Writes progress to training_progress.json for frontend polling."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROGRESS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "training_progress.json")


def write_progress(status, **kwargs):
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump({"status": status, **kwargs}, f)
    except Exception:
        pass


def main():
    try:
        data = json.load(sys.stdin)
        model_type = data.get("model_type", "advanced")
        epochs = int(data.get("epochs", 15))
        batch_size = int(data.get("batch_size", 128))

        from tensorflow import keras
        from model import load_mnist_data, build_cnn_model, build_simple_model, train_model
        from predictor import get_predictor
        from config import MODEL_PATH

        write_progress("loading", message="Loading MNIST data...")
        (x_train, y_train), (x_test, y_test) = load_mnist_data()

        write_progress("building", message="Building model...")
        model = build_simple_model() if model_type.lower() == "simple" else build_cnn_model()

        # Callback to write epoch progress
        def on_epoch_end(epoch, logs=None):
            logs = logs or {}
            write_progress(
                "training",
                current_epoch=epoch + 1,
                total_epochs=epochs,
                loss=float(logs.get("loss", 0)),
                acc=float(logs.get("accuracy", logs.get("acc", 0))),
                val_loss=float(logs.get("val_loss", 0)),
                val_acc=float(logs.get("val_accuracy", logs.get("val_acc", 0))),
            )

        # We need to inject our callback - train_model uses model.fit internally
        # So we patch or use a wrapper. Easiest: call model.fit ourselves with extra callback
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=1e-3),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1
        )
        early_stop = keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=5, restore_best_weights=True, verbose=1
        )
        progress_cb = keras.callbacks.LambdaCallback(
            on_epoch_end=lambda e, l: on_epoch_end(e, l or {})
        )

        write_progress("training", current_epoch=0, total_epochs=epochs, message="Starting training...")
        history = model.fit(
            x_train, y_train,
            batch_size=batch_size,
            epochs=epochs,
            validation_split=0.1,
            callbacks=[reduce_lr, early_stop, progress_cb],
            verbose=1,
        )

        write_progress("evaluating", message="Evaluating on test set...")
        test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)

        model.save(MODEL_PATH)
        get_predictor(model_path=MODEL_PATH).set_model(model)

        write_progress("done", test_accuracy=float(test_acc), test_loss=float(test_loss))
        print(json.dumps({
            "test_accuracy": float(test_acc),
            "test_loss": float(test_loss),
        }))
    except Exception as e:
        write_progress("error", error=str(e))
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
