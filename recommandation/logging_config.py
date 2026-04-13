# recommandation/logging_config.py
"""
Configuration de logging pour le système de recommandation.

À inclure dans djib_reco/settings.py :

    from recommandation.logging_config import LOGGING

Cela active:
  - Logs DEBUG/INFO/WARNING/ERROR du module recommandation
  - Sortie Console avec timestamps
  - Filtrage par niveau
"""

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name}: {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/recommandation.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 5,
            'formatter': 'verbose',
            'level': 'INFO',
        },
    },
    'loggers': {
        'recommandation': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'recommandation.engine': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'recommandation.views': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Exemple de logs attendus:
SAMPLE_LOGS = """
[INFO] 2026-04-13 14:23:45 recommandation.engine: [MatriceConstruction] 15 users, 40 avis, 45 favoris, 80 interactions (temps: 0.12s)
[INFO] 2026-04-13 14:23:45 recommandation.engine: [RecoMotor] User 5: 8 voisins, 6 recommendations (temps: 0.024s)
[INFO] 2026-04-13 14:23:46 recommandation.views: [RecoAPI:recommandations] Début pour user 5 (nb=6)
[INFO] 2026-04-13 14:23:46 recommandation.views: [RecoAPI:recommandations] Calcul 6 resultats (0.034s)
[DEBUG] 2026-04-13 14:23:47 recommandation.engine: [Interaction] user 5 → resto 12 [vue]
[INFO] 2026-04-13 14:23:47 recommandation.views: [RecoAPI:interaction] user 5 → resto 12 [vue] (0.008s)
"""
