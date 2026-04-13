# 📊 Monitoring des Algorithmes Hybrides

Guide pour monitorer et déboguer le système de recommandation multi-algorithme (CF, CB, Hybrid).

---

## 1. Endpoints de Debug

### A/B Testing : Comparer tous les algorithmes

```bash
# Pour l'utilisateur connecté
curl -H "Authorization: Bearer <token>" \
  https://djib-reco.onrender.com/recommandations/comparer/?nb=6

# Réponse : 5 listes de recommandations côte à côte
{
  "comparaison": {
    "cf": [{id, nom, note, ...}, ...],       # Collaborative Filtering
    "cb": [{id, nom, note, ...}, ...],       # Content-Based
    "hybrid_weighted": [...],                 # Weighted (60% CF, 40% CB)
    "hybrid_switching": [...],                # Adaptive (CF ou CB)
    "hybrid_augmented": [...]                 # Feature-Augmented
  },
  "user_coverage": {
    "used_cf": true,              # Peut utiliser CF?
    "used_cb": true,              # Peut utiliser CB?
    "interaction_count": 15,      # Nombre d'interactions
    "avis_count": 8,              # Nombre d'avis
    "cold_start": false,          # Est en cold-start?
    "recommendation_status": "warm_cf"  # CF/CB/cold_start
  }
}
```

### Analyse de couverture utilisateur

```bash
# Comprendre quel algorithme peut servir un utilisateur
curl -H "Authorization: Bearer <token>" \
  https://djib-reco.onrender.com/recommandations/analyse/

# Réponse
{
  "couverture": {
    "used_cf": true,
    "used_cb": true,
    "interaction_count": 15,
    "avis_count": 8,
    "cold_start": false,
    "recommendation_status": "warm_cf"
  }
}
```

---

## 2. Métriques de Performance

### Temps d'exécution par algorithme

| Algorithme | Temps moyen | Plage | Notes |
|-----------|-----------|-------|-------|
| CF (Collaborative) | 150-300ms | 100-500ms | Zoom selon taille matrice |
| CB (Content-Based) | 200-400ms | 150-600ms | Zoom selon interactions |
| Hybrid (Weighted) | 300-600ms | 250-800ms | CF + CB combinés |
| Hybrid (Switching) | 150-400ms | 100-500ms | CF OU CB (pas les deux) |
| Hybrid (Augmented) | 250-500ms | 200-700ms | CF enrichi avec CB |

**Optimisation** : Toujours utiliser le cache (TTL 1h) quand possible :

```json
[RecoAPI:recommandations] Cache HIT 6 resultats (0.052s)
```

### Distribution des stratégies par type d'utilisateur

```
Cold-start (0-2 avis)      → Switching: CB (200-400ms)
↓
Warm CB (2-5 avis)         → Switching: CB (200-400ms) 
↓
Warm CF (5+ avis)          → Switching: CF (150-300ms) ou Hybrid (300-600ms)
↓
Very Warm (20+ avis)       → CF direct ou Hybrid Weighted (150-500ms)
```

---

## 3. Logs par Algorithme

### Format standard

Tous les logs incluent:
- Timestamp `[YYYY-MM-DD HH:MM:SS]`
- Module `[RecoAPI] ou [ENGINE]`
- Opération `[operation]`
- User ID `user_X`
- Timing `(0.234s)`

### Content-Based Filtering

```
[ContentEngine:ExtractFeatures] resto 12 en 0.003s
[ContentEngine:ProfilUtilisateur] user 5 3 restaurants (temps: 0.042s)
[ContentEngine:Recommander] user 5 → 6 recommendations (temps: 0.156s)
```

### Hybrid Filtering

```
[HybridEngine:Recommander] user 5 cold-start (CB mode)
[HybridEngine:Recommander] 6 recommendations en 0.234s (switching→CB)

[HybridEngine:Recommander] user 8 warm user (CF mode)
[HybridEngine:Recommander] 6 recommendations en 0.187s (switching→CF)

[HybridEngine:Recommander] 4 recommendations en 0.456s (weighted α=0.6)
[HybridEngine:Recommander] 5 recommendations en 0.512s (feature_augmented)

[HybridEngine:Comparer] user 5 comparison en 1.234s
```

### API Endpoints

```
[RecoAPI:content-based] Début pour user 5 (nb=6)
[RecoAPI:content-based] Retourné 6 resultats (0.234s)

[RecoAPI:hybride] Début user 8 (nb=6, alpha=0.6, strategy=weighted)
[RecoAPI:hybride] Retourné 6 resultats (0.456s, strategy=weighted)

[RecoAPI:comparer] Début pour user 5
[RecoAPI:comparer] Comparaison complète (1.234s)

[RecoAPI:analyse] Analyse user 5
[RecoAPI:analyse] Analyse complète (0.045s)
```

---

## 4. Alertes & Thresholds

### Performance Alerts

| Seuil | Algorithme | Action |
|-------|-----------|--------|
| > 1s | Toute requête | ⚠️ Log warning, check matrice size |
| > 2s | Toute requête | 🚨 Log error, possible timeout |
| > CPU 80% | CF (matrice) | 🚨 Fragmenter calcul ou implémenter pré-calcul |

### Ejemplo de détection

```python
# Dans logging_config.py ou custom middleware
if elapsed > 1.0:
    logger.warning(f'[SlowReco] {algo} took {elapsed:.2f}s for user {user_id}')
    
if elapsed > 2.0:
    logger.error(f'[TimeoutReco] {algo} TIMEOUT {elapsed:.2f}s for user {user_id}')
```

### Cold-start Detection

```
[ContentEngine:ProfilUtilisateur] user 3 pas de préférence
→ User n'a aucun avis 4+ stars
→ Fallback: CB avec faibles scores ou top global

[HybridEngine:Recommander] user 3 cold-start (CB mode)
→ User a < 3 interactions
→ Recommandé: Content-Based seulement
```

---

## 5. Analytics & Reporting

### Requête pour compter algorithmes 

```sql
-- Combien de user par status?
SELECT 
  status IN ('cold_start') as is_cold_start,
  COUNT(*) as count
FROM (
  SELECT DISTINCT 
    user_id,
    CASE 
      WHEN interaction_count < 3 AND avis_count < 2 THEN 'cold_start'
      WHEN avis_count < 3 THEN 'warm_cb'
      ELSE 'warm_cf'
    END as status
  FROM (
    SELECT 
      u.id as user_id,
      COUNT(DISTINCT i.id) as interaction_count,
      COUNT(DISTINCT a.id) as avis_count
    FROM auth_user u
    LEFT JOIN recommandation_interactionutilisateur i ON u.id = i.utilisateur_id
    LEFT JOIN restaurants_avis a ON u.id = a.utilisateur_id
    GROUP BY u.id
  ) subq
) subq2
GROUP BY is_cold_start;
```

### Cache Hit Rate (via logs)

```bash
# Compter hits vs calculs
grep -c "Cache HIT" access.log           # Total hits
grep -c "Calcul" access.log             # Total misses

# Hit rate = hits / (hits + misses)
# Target: > 80% pour production
```

---

## 6. Admin Panel Integration

### Dashboard interactif

Via `/admin/recommandation/cacherecommandation/` :

- **Liste** : Voir cache pour chaque user avec:
  - Nombre de recommandations
  - Âge du cache (frais/expiré)
  - Quel algorithme peut servir
  
- **Détail** : Pour chaque user:
  - Analyse complète de couverture
  - Status CF/CB/Hybrid
  - Nombre interactions vs avis
  - IDs recommandés actuels

### Monitoring Interactions

Via `/admin/recommandation/interactionutilisateur/` :

- Type d'action avec couleur (vue/clic/partage)
- Timeline (date_hierarchy)
- Filtrer par type et date
- Chercher par user/restaurant

---

## 7. Debugging Common Issues

### "User has 0 recommendations"

❌ Problème : Tous les restaurants sont déjà notés
✅ Vérifier : 
```python
# user_id 5 a noté combien?
from restaurants.models import Avis
Avis.objects.filter(utilisateur_id=5).count()

# Combien de restaurants total?
from restaurants.models import Restaurant
Restaurant.objects.filter(est_ouvert=True).count()

# Si count(avis) > count(restaurants), problème
```

### "Hybrid switching stuck on CB"

❌ Problème : User reste en cold-start même avec interactions
✅ Vérifier :
```python
# CF dépend des AVIS, pas interactions
from restaurants.models import Avis
from recommandation.models import InteractionUtilisateur

user_id = 5
avis = Avis.objects.filter(utilisateur_id=user_id).count()        # Doit être >= 2
inter = InteractionUtilisateur.objects.filter(utilisateur_id=user_id).count()
# Inter >= 3 n'active CF, c'est AVIS qui compte!
```

❌ Bug dans Hybrid: 
```python
# INCORRECT:
if interaction_count < 3:
    use_cb()  # ← Mauvais, ignores avis
    
# CORRECT:
if interaction_count < 3 AND avis_count < 2:
    use_cb()  # ← Bon, check les deux signaux
```

### "Cache not invalidating"

❌ Problème : User vient d'à ajouter avis, mais cache pas à jour
✅ Vérifier signals :
```python
# Dans recommandation/signals.py, post_save sur Avis doit invalider:
cache = CacheRecommandation.objects.filter(utilisateur=avis.utilisateur)
cache.delete()  # ← Doit  être appelé

# Test:
from recommandation.models import CacheRecommandation
CacheRecommandation.objects.filter(utilisateur_id=5).exists()
# Doit retourner False après ajout avis
```

---

## 8. Production Checklist

- [ ] [LOGGING] Configure logging dans `settings.py`
- [ ] [CACHE] TTL set to 1 hour (CACHE_TTL_MINUTES = 60)
- [ ] [ADMIN] Admin panel accessible pour monitoring
- [ ] [TESTS] All 68 tests passing
- [ ] [PERFORMANCE] Benchmark cold-start vs warm users
- [ ] [UPTIME] Monitor API endpoints response times
- [ ] [ALERTS] Set up error tracking (Sentry/similar)
- [ ] [A/B TEST] Decide default strategy (recommend: hybrid_switching)

