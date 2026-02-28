from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root),
    path('health', views.health),
    path('config', views.model_status),
    path('model/status', views.model_status),
    path('predict', views.predict_file),
    path('predict/base64', views.predict_base64),
    path('train', views.train),
    path('samples', views.samples),
    path('evaluate', views.evaluate),
    path('predictions', views.prediction_list),
    path('training-runs', views.training_run_list),
]