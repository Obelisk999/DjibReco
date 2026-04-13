import logging
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djib_reco.settings')

application = get_wsgi_application()

# Vercel's @vercel/python runtime looks for a variable named `app`.
app = application
