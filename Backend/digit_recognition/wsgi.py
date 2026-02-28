"""
WSGI config for digit recognition project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_recognition.settings')

application = get_wsgi_application()
