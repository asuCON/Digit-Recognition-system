"""
Database models for MNIST Digit Recognition.
Stores predictions, training runs, and audit data in MySQL.
"""

from django.db import models


class TrainingRun(models.Model):
    """Records each model training session."""
    model_type = models.CharField(max_length=32, choices=[
        ('advanced', 'Advanced CNN'),
        ('simple', 'Simple CNN'),
    ])
    epochs = models.PositiveIntegerField()
    batch_size = models.PositiveIntegerField()
    test_accuracy = models.FloatField()
    test_loss = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'digit_training_runs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.model_type} - {self.test_accuracy:.2%} @ {self.created_at}"


class Prediction(models.Model):
    """Stores each digit prediction for analytics and history."""
    digit = models.PositiveSmallIntegerField()
    confidence = models.FloatField()
    source = models.CharField(max_length=16, choices=[
        ('file', 'File Upload'),
        ('canvas', 'Canvas/Base64'),
    ])
    image_data = models.TextField(blank=True, null=True)  # Optional base64 thumbnail (compressed)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'digit_predictions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Digit {self.digit} ({self.confidence:.2%})"


class PredictionProbability(models.Model):
    """Stores per-class probabilities for each prediction (optional detail)."""
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='probabilities')
    digit_class = models.PositiveSmallIntegerField()
    probability = models.FloatField()

    class Meta:
        db_table = 'digit_prediction_probabilities'
        unique_together = ['prediction', 'digit_class']
