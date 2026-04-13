"""
WSGI config for djib_reco project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import logging
import os
import sqlite3

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djib_reco.settings')

application = get_wsgi_application()

# Sur Vercel chaque invocation dispose d'un /tmp isolé et vide (SQLite éphémère).
# On applique les migrations au démarrage pour que toutes les tables existent.
# Note : les instances Vercel sont isolées, donc pas de race condition sur /tmp.
from django.conf import settings  # noqa: E402
if not settings.DEBUG and 'sqlite3' in settings.DATABASES['default']['ENGINE']:
    _logger = logging.getLogger(__name__)
    try:
        _db_path = str(settings.DATABASES['default']['NAME'])
        _conn = sqlite3.connect(_db_path)
        _tables = _conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        _conn.close()
        if not _tables:
            from django.core.management import call_command
            call_command('migrate', '--noinput', verbosity=0)
    except Exception as exc:
        _logger.error("Échec de l'initialisation de la base SQLite au démarrage : %s", exc)
