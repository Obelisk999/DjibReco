"""
recommandation/apps.py
"""
from django.apps import AppConfig


class RecommandationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name               = 'recommandation'
    verbose_name       = 'Système de recommandation'

    def ready(self):
        import recommandation.signals  # noqa: F401 — enregistre les signaux
