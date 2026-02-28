from django.apps import AppConfig


class DigitApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'digit_api'
    verbose_name = 'MNIST Digit Recognition API'
