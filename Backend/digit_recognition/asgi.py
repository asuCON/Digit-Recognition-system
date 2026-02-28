"""
ASGI config for digit recognition project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_recognition.settings')

application = get_asgi_application()
