"""
DRF Serializers for digit_api.
"""
from rest_framework import serializers
from .models import Prediction, TrainingRun, PredictionProbability


class PredictionProbabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionProbability
        fields = ['digit_class', 'probability']


class PredictionSerializer(serializers.ModelSerializer):
    probabilities = PredictionProbabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Prediction
        fields = ['id', 'digit', 'confidence', 'source', 'created_at', 'probabilities']


class TrainingRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingRun
        fields = ['id', 'model_type', 'epochs', 'batch_size', 'test_accuracy', 'test_loss', 'created_at']
