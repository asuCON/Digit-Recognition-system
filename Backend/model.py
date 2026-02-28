"""
Advanced MNIST Digit Recognition - CNN Model
Uses a Convolutional Neural Network with data augmentation for improved accuracy.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.datasets import mnist


def load_mnist_data():
    """Load and preprocess MNIST dataset."""
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    # Normalize pixel values to [0, 1] and add channel dimension
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0
    x_train = np.expand_dims(x_train, -1)
    x_test = np.expand_dims(x_test, -1)
    
    # One-hot encode labels
    y_train = keras.utils.to_categorical(y_train, 10)
    y_test = keras.utils.to_categorical(y_test, 10)
    
    return (x_train, y_train), (x_test, y_test)


def create_data_augmentation():
    """Create data augmentation pipeline for improved generalization."""
    return keras.Sequential([
        layers.RandomRotation(factor=0.12, fill_mode="constant", fill_value=0),
        layers.RandomZoom(height_factor=0.15, width_factor=0.15, fill_mode="constant", fill_value=0),
        layers.RandomTranslation(height_factor=0.12, width_factor=0.12, fill_mode="constant", fill_value=0),
    ])


def _residual_block(x, filters, strides=1):
    """Residual block with skip connection."""
    shortcut = x
    x = layers.Conv2D(filters, (3, 3), strides=strides, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Conv2D(filters, (3, 3), padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    if strides > 1 or shortcut.shape[-1] != filters:
        shortcut = layers.Conv2D(filters, (1, 1), strides=strides, use_bias=False)(shortcut)
        shortcut = layers.BatchNormalization()(shortcut)
    x = layers.Add()([x, shortcut])
    x = layers.Activation("relu")(x)
    return x


def build_cnn_model(input_shape=(28, 28, 1), num_classes=10):
    """
    Advanced CNN with residual blocks, deeper architecture, and data augmentation.
    - Residual connections for gradient flow
    - 4 convolutional blocks with BatchNorm and Dropout
    - GlobalAveragePooling for parameter efficiency
    - Dense head with regularization
    """
    inputs = keras.Input(shape=input_shape)
    x = create_data_augmentation()(inputs)

    # Initial conv
    x = layers.Conv2D(32, (3, 3), padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Conv2D(32, (3, 3), strides=2, padding="same", use_bias=False)(x)
    x = layers.BatchNormalization()(x)
    x = layers.Activation("relu")(x)
    x = layers.Dropout(0.2)(x)

    # Residual block 1 (32 filters)
    x = _residual_block(x, 32)
    x = layers.Dropout(0.2)(x)

    # Downsample + residual block 2 (64 filters)
    x = _residual_block(x, 64, strides=2)
    x = layers.Dropout(0.25)(x)

    # Residual block 3 (128 filters)
    x = _residual_block(x, 128, strides=2)
    x = layers.Dropout(0.3)(x)

    # Residual block 4 (256 filters)
    x = _residual_block(x, 256)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.5)(x)

    # Dense head
    x = layers.Dense(512, activation="relu", kernel_regularizer=keras.regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation="relu", kernel_regularizer=keras.regularizers.l2(1e-4))(x)
    x = layers.Dropout(0.4)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = keras.Model(inputs=inputs, outputs=outputs)
    return model


def build_simple_model(input_shape=(28, 28, 1), num_classes=10):
    """Build a simpler/faster model for quick training."""
    model = keras.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation="relu"),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax"),
    ])
    return model


def train_model(model, x_train, y_train, x_test, y_test, 
                epochs=15, batch_size=128, use_augmentation=True):
    """Train the model with optional augmentation."""
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    
    # Reduce learning rate on plateau
    reduce_lr = keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6, verbose=1
    )
    
    # Early stopping
    early_stop = keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=5, restore_best_weights=True, verbose=1
    )
    
    callbacks = [reduce_lr, early_stop]
    
    history = model.fit(
        x_train, y_train,
        batch_size=batch_size,
        epochs=epochs,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1,
    )
    
    # Final evaluation
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    return history, test_loss, test_acc


def predict_digit(model, image_array):
    """
    Predict digit from image array.
    Expects image normalized to 28x28 grayscale (values 0-1).
    """
    if len(image_array.shape) == 2:
        image_array = np.expand_dims(np.expand_dims(image_array, -1), 0)
    elif len(image_array.shape) == 3:
        image_array = np.expand_dims(image_array, 0)
    
    predictions = model.predict(image_array, verbose=0)
    return predictions[0]


def prepare_image_for_prediction(image):
    """
    Prepare image for model prediction.
    Accepts PIL Image or numpy array, resizes to 28x28, inverts if needed (dark on light).
    For programmatic use, prefer preprocessing.preprocess().
    """
    from preprocessing import preprocess
    return preprocess(image)
