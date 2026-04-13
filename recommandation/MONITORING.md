# recommandation/MONITORING.md

# 📊 Monitoring & Logging - Système de Recommandation

## Configuration rapide

### 1. Ajouter le logging au `settings.py`

```python
# djib_reco/settings.py
import os
from pathlib import Path

# Créer le répertoire logs s'il n'existe pas
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Importer la configuration de logging
from recommandation.logging_config import LOGGING

# LOGGING est maintenant disponible pour Django
```

### 2. Assurez-vous que le répertoire `logs/` existe

```bash
mkdir -p logs/
```

### 3. Vérifier les logs en temps réel

```bash
# Terminal 1: Démarrer Django
python manage.py runserver

# Terminal 2: Suivre les logs
tail -f logs/recommandation.log
```

---

## Métriques clés

### 1. Temps de réponse API

Chaque endpoint enregistre son temps d'exécution:

```
[INFO] [RecoAPI:recommandations] Calcul 6 resultats (0.034s)
```

| Endpoint | Temps attendu | Limite critique |
|----------|---------------|-----------------|
| GET /recommandations/pour-moi/ | < 200ms | > 1000ms |
| POST /recommandations/interaction/ | < 10ms | > 100ms |
| GET /recommandations/similaires/ | < 100ms | > 500ms |

### 2. Efficacité du cache

```
[INFO] [RecoAPI:recommandations] Cache HIT 6 resultats (0.052s)
[INFO] [RecoAPI:recommandations] Calcul 6 resultats (0.034s)
```

**Ratio ideal** : > 80% cache hit (moins de calculs)

### 3. État du cold-start

```
[INFO] [RecoMotor] Cold-start pour user 10 (2 interactions < 3)
```

Si beaucoup d'utilisateurs sont en cold-start → les données sont insuffisantes

### 4. Performance du moteur

```
[INFO] [MatriceConstruction] 25 users, 214 avis, 48 favoris, 92 interactions (temps: 0.325s)
[INFO] [RecoMotor] User 5: 8 voisins, 6 recommendations (temps: 0.024s)
```

- Matrice: O(n) où n = total interactions
- Recommandation: O(m*k) où m = # users, k = # voisins

---

## Niveaux de log

### DEBUG (très détaillé)

```
[DEBUG] [Interaction] user 5 → resto 12 [vue]
```

Utilisé pour:
- Chaque interaction enregistrée
- Entrées/sorties de fonction détaillées

### INFO (normal)

```
[INFO] [RecoAPI:recommandations] Calcul 6 resultats (0.034s)
[INFO] [RecoMotor] User 5: 8 voisins, 6 recommendations (temps: 0.024s)
```

Utilisé pour:
- Appels API
- Décisions algo (CF vs cold-start)
- Performances critiques

### WARNING (à surveiller)

```
[WARNING] [RecoMotor] Aucun voisin similaire pour user 10
[WARNING] [Interaction] Impossible d'enregistrer interaction
```

Utilisé pour:
- Données manquantes
- Cas limites non critiques

### ERROR (problème)

```
[ERROR] [RecoAPI:recommandations] ERREUR user 5: Division by zero (0.015s)
```

Utilisé pour:
- Exceptions non gérées
- Accès BD échoués
- Erreurs de configuration

---

## Alertes importantes

### ⚠️ Trop d'utilisateurs en cold-start

**Signal**: Plusieurs logs:
```
[INFO] [RecoMotor] Cold-start pour user X (2 interactions < 3)
```

**Cause**: Pas assez d'interaction données collectées  
**Action**: 
1. Vérifier que `reco_tracker.js` est actif
2. Vérifier que les utilisateurs sont authentifiés
3. Augmenter les données de test: `python manage.py create_test_interactions --users 50`

### ⚠️ Cache jamais invalidé

**Signal**: Toujours `"source": "cache"` dans les réponses  
**Cause**: Signaux Django non connectés  
**Action**:
1. Vérifier que `INSTALLED_APPS` contient `'recommandation'`
2. Vérifier que `recommandation/apps.py` appelle `import recommandation.signals`

### ⚠️ API très lente

**Signal**: Logs montrent > 500ms
```
[INFO] [RecoAPI:recommandations] Calcul 6 resultats (1.234s)
```

**Cause**: 
1. Trop d'utilisateurs/restaurants en BD
2. Requête BD inefficace

**Action**:
1. Vérifier les indexes: `python manage.py sqlsequencereset restaurants | python manage.py dbshell`
2. Limiter nb d'utilisateurs: chercher N_VOISINS dans `engine.py`

---

## Scraper les logs

### Compter les appels API par type

```bash
grep "\[RecoAPI" logs/recommandation.log | wc -l
```

### Temps moyen de réponse

```bash
grep "\[RecoAPI:recommandations\]" logs/recommandation.log | \
  grep -oP '\(\K[0-9.]+(?=s\))' | \
  awk '{sum+=$1; count++} END {print sum/count " s"}'
```

### Erreurs dans les 24h

```bash
grep "\[ERROR\]" logs/recommandation.log | tail -100
```

### Cold-start ratio

```bash
grep "Cold-start pour user" logs/recommandation.log | wc -l  # N cold-starts
grep "\[RecoMotor\] User" logs/recommandation.log | wc -l     # Total recommandations
```

---

## Dashboard simple (optionnel)

Vous pouvez créer un endpoint pour afficher les logs:

```python
# recommandation/views.py
@login_required
def dashboard_reco(request):
    """Affiche les stats du système de recommandation."""
    if not request.user.is_staff:
        return HttpResponseForbidden('Accès admin requis')
    
    # Lire les logs
    try:
        with open('logs/recommandation.log', 'r') as f:
            lines = f.read().split('\n')[-50:]  # Derniers 50 logs
    except:
        lines = []
    
    # Compter les stats
    stats = {
        'total_users': User.objects.count(),
        'total_interactions': InteractionUtilisateur.objects.count(),
        'cache_size': CacheRecommandation.objects.count(),
    }
    
    return render(request, 'recommandation/dashboard.html', {
        'logs': lines,
        'stats': stats,
    })
```

Template `templates/recommandation/dashboard.html`:

```html
{% extends 'base.html' %}
{% block content %}
<div class="container py-4">
    <h1>📊 Recommandation Dashboard</h1>
    
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h6>Utilisateurs</h6>
                    <h3>{{ stats.total_users }}</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h6>Interactions</h6>
                    <h3>{{ stats.total_interactions }}</h3>
                </div>
            </div>
        </div>
    </div>
    
    <h2>Derniers logs</h2>
    <pre style="background: #f5f5f5; padding: 1rem; overflow: auto; height: 400px;">{% for line in logs %}{{ line }}
{% endfor %}</pre>
</div>
{% endblock %}
```

---

## Checklist de production

- [ ] Logging configuré dans `settings.py`
- [ ] Répertoire `logs/` existe et est accessible en écriture
- [ ] Rotation de logs activée (`.handlers.RotatingFileHandler`)
- [ ] Cache expiration correcte (CACHE_TTL_MINUTES = 60)
- [ ] Interactions implicites sont enregistrées
- [ ] Signaux Django invalidant le cache fonctionnent
- [ ] Tests passent: `python manage.py test recommandation.tests`
- [ ] Logs monitorés: `tail -f logs/recommandation.log`
- [ ] Alertes configurées pour WARNING/ERROR

---

**Document**: MONITORING.md | Date: 13 avril 2026
