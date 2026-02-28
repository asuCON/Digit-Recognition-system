"""
Django admin for digit_api models.
"""
from django.contrib import admin
from .models import Prediction, TrainingRun, PredictionProbability


class PredictionProbabilityInline(admin.TabularInline):
    model = PredictionProbability
    extra = 0


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ['id', 'digit', 'confidence', 'source', 'created_at']
    list_filter = ['source', 'digit']
    inlines = [PredictionProbabilityInline]


@admin.register(TrainingRun)
class TrainingRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'model_type', 'epochs', 'batch_size', 'test_accuracy', 'test_loss', 'created_at']
    list_filter = ['model_type']
