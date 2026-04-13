# ⚡ Quick Start : Recommandations 3 Algorithmes

Guide ultra-rapide pour tester les 3 systèmes de recommandation.

---

## 1️⃣ Collaborative Filtering (Défaut)

**Quand l'utiliser** : Utilisateurs avec historique (5+ avis)

```bash
# Demander des recommandations CF
curl -H "Authorization: Bearer TOKEN" \
  https://djib-reco.onrender.com/recommandations/pour-moi/?nb=6
  
# Réponse: 6 restaurants basés sur voisins similaires
```

**Cas d'usage**:
- ✅ Utilisateurs réguliers avec historique
- ✅ Personnes qui aiment les "découvertes de voisins"
- ❌ Froids (0 avis)

**Perfs**: 150-300ms en moyenne

---

## 2️⃣ Content-Based Filtering

**Quand l'utiliser** : Baseline / Cold-start / Découverte

```bash
# Recommandations basées sur features (catégorie, prix, localité)
curl -H "Authorization: Bearer TOKEN" \
  https://djib-reco.onrender.com/recommandations/content-based/?nb=6

# Réponse: 6 restaurants similaires à l'historique de l'user
```

**Features utilisées**:
- 🏷️ Catégorie (40%)
- 💰 Prix (25%)
- 📍 Localité (20%)
- 🔖 Tags (15%)

**Cas d'usage**:
- ✅ Utilisateurs nouveaux (< 2 avis)
- ✅ Découverte de restaurants similaires
- ✅ A/B testing (baseline)

**Perfs**: 200-400ms

---

## 3️⃣ Hybrid Filtering (Recommandé)

**Quand l'utiliser** : PARTOUT - le meilleur compromis

```bash
# Version 1: Weighted (défaut 60% CF, 40% CB)
curl -H "Authorization: Bearer TOKEN" \
  'https://djib-reco.onrender.com/recommandations/hybride/?strategy=weighted&alpha=0.6'

# Version 2: Switching (CF si user warm, CB si cold)  
curl -H "Authorization: Bearer TOKEN" \
  'https://djib-reco.onrender.com/recommandations/hybride/?strategy=switching'

# Version 3: Feature-Augmented (CF + CB fusion)
curl -H "Authorization: Bearer TOKEN" \
  'https://djib-reco.onrender.com/recommandations/hybride/?strategy=feature_augmented'
```

**Stratégies**:

| Stratégie | Format | Meilleur pour |
|-----------|--------|---------------|
| **Weighted** | α*CF + (1-α)*CB | A/B testing, tuning |
| **Switching** | CF OR CB (auto) | Production (adaptatif) |
| **Augmented** | CF + CB features | Qualité max, plus lent |

**Perfs**:
- Switching: 150-400ms (plus rapide)
- Weighted: 300-600ms  
- Augmented: 250-500ms

---

## 🧪 A/B Testing : Comparer les 3

```bash
# Voir les 5 listes côte à côte pour même user
curl -H "Authorization: Bearer TOKEN" \
  https://djib-reco.onrender.com/recommandations/comparer/?nb=6

# Réponse
{
  "comparaison": {
    "cf": [{id, nom, note, ...}],
    "cb": [{id, nom, note, ...}],
    "hybrid_weighted": [{...}],
    "hybrid_switching": [{...}],
    "hybrid_augmented": [{...}]
  },
  "user_coverage": {
    "cold_start": false,
    "recommendation_status": "warm_cf"
  }
}
```

**Usage**:
1. Appeler cet endpoint pour 5-10 utilisateurs
2. Comparer visuellement les résultats
3. Choisir la meilleure stratégie
4. A/B test en production pendant 2-4 semaines

---

## 🔍 Analyser un Utilisateur Spécifique

```bash
# Quel algorithme peut servir cet user?
curl -H "Authorization: Bearer TOKEN" \
  https://djib-reco.onrender.com/recommandations/analyse/

# Réponse
{
  "couverture": {
    "used_cf": true,          # CF possible?
    "used_cb": true,          # CB possible?
    "interaction_count": 15,  # Interactions implicites
    "avis_count": 8,          # Avis explicites
    "cold_start": false,      # Est neuf?
    "recommendation_status": "warm_cf"  # CF/CB/cold_start
  }
}
```

**Interprétation**:
- `cold_start: true` → Démarrage à froid, utiliser CB
- `warm_cf` → Utilisateur chaud, CF optimal
- `warm_cb` → Peu d'interactions, CB meilleur

---

## 📊 Dashboard Admin

Allez à `/admin/recommandation/cacherecommandation/` pour voir:

✅ Cache status (frais/expiré)
✅ Quel algorithme pour chaque user
✅ Nombre d'interactions/avis
✅ IDs recommandés actuels

---

## 🚀 Production Defaults

```python
# Recommendation pour production (dans settings.py ou env)

RECO_DEFAULT_STRATEGY = 'switching'  # Adaptatif
RECO_DEFAULT_ALPHA = 0.6             # 60% CF, 40% CB (si weighted)
RECO_CACHE_TTL = 60                  # 1 heure
```

---

## 📈 Metriques à Tracker

- **Response Time**: < 500ms (p95)
- **Cache Hit Rate**: > 80%
- **Algorithm Breakdown**:
  - % users in cold-start
  - % users warm_cf vs warm_cb
  - % using hybrid vs pure

---

## ❓ FAQ Rapide

**Q: Quel algorithme choisir?**  
A: **Hybrid Switching** - Adaptatif, zéro config

**Q: Pourquoi CF + CB au lieu de CF seul?**  
A: CF échoue au cold-start (< 3 interactions), CB toujours OK

**Q: Pourquoi la fusion ne fait pas l'average simple?**  
A: Weighted + Switching couvrent plus de cas; Feature-Augmented meilleure qualité

**Q: Cache invalidation?**  
A: Auto via signals.py - cache invalide si user ajoute avis/favori

**Q: Performance concern?**  
A: Cache TTL 1h = 80% hits, reste rapide

---

## 🔗 Plus de Docs

- [README.md](README.md) - Architecture complète
- [MONITORING_HYBRID.md](MONITORING_HYBRID.md) - Logs & debugging
- [tests.py](tests.py) - 68 tests (source de vérité)

