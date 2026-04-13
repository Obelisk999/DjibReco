# 🎯 Système de Recommandation DjibReco

## Vue d'ensemble

Le système de recommandation de DjibReco utilise un **filtrage collaboratif user-based** avec **fallback Wilson score** pour suggérer des restaurants personnalisés à chaque utilisateur.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (JS)                          │
│  - reco_tracker.js: Enregistrement interactions implicites   │
│  - main.js: Gestion du DOM                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                  POST /recommandations/interaction/
                  (vue, clic_menu, partage)
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      DJANGO VIEWS                           │
│  - recommandations_pour_moi: API personnalisée             │
│  - enregistrer_interaction_view: Log interactions            │
│  - restaurants_similaires_view: Item-based                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     MOTEUR (engine.py)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. construire_matrice()                              │   │
│  │    → Agrège tous les signaux utilisateur-restaurant  │   │
│  │    → Avis (1-5), Favoris (+4), Vues (+1), Clics     │   │
│  │    → Scores plafonnés à 10                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 2. recommander_pour_utilisateur(user_id)            │   │
│  │    → Calcule similarité cosinus vs tous les autres  │   │
│  │    → Agrège scores des 10 voisins les plus proches  │   │
│  │    → Cold-start: fallback top global (Wilson score) │   │
│  │    → Exclut restaurants déjà notés/consultés       │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 3. restaurants_similaires(restaurant_id)            │   │
│  │    → Item-based: trouve co-ratings                  │   │
│  │    → Utilisateurs qui aiment ce resto ont aimé...  │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                       BASE DE DONNÉES                       │
│  - InteractionUtilisateur (vue, clic_menu, partage)         │
│  - CacheRecommandation (TTL 1 heure)                        │
│  - Avis (notes 1-5)                                         │
│  - Favori (0 ou 1)                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration

### 1. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 2. Migrations Django

```bash
python manage.py migrate recommandation
```

### 3. Variables d'environnement (`.env`)

Aucune variable spéciale requise. Le système fonctionne avec la config par défaut.

Optionnel pour ajuster :
```env
# recommandation/engine.py (paramètres de l'algo)
RECO_SEUIL_COLD_START=3      # Min interactions avant CF
RECO_NB_VOISINS=10           # K-neighbors collaboratif
RECO_NB_DEFAULT=6            # Résultats par défaut
```

---

## Utilisation

### A. Frontend - Enregistrer les interactions

#### 1. Tracking automatique (page détail restaurant)

Le script `reco_tracker.js` enregistre automatiquement une **"vue"** lors de l'accès à une page de détail :

```html
<!-- templates/restaurants/detail.html -->
<div data-restaurant-id="{{ restaurant.id }}" data-page="detail">
  <!-- Le tracking démarre automatiquement après 1.5s -->
</div>
```

#### 2. Tracking des clics menu

```html
<button data-clic-menu data-restaurant-id="{{ restaurant.id }}">
  Voir le plat
</button>

<!-- Script JavaScript auto-déclenché dans reco_tracker.js -->
```

#### 3. Tracking des partages (optionnel)

```html
<button data-partage data-restaurant-id="{{ restaurant.id }}">
  Partager
</button>
```

### B. API REST

Tous les endpoints sont en JSON et incluent la validation automatique.

#### 1. Recommandations personnalisées

```bash
# GET - Récupère les 6 restaurants recommandés pour l'utilisateur connecté
curl -H "Authorization: Bearer <token>" \
  https://djib-reco.onrender.com/recommandations/pour-moi/?nb=6

# Réponse
{
  "recommandations": [
    {
      "id": 12,
      "nom": "Chez Giovanni",
      "slug": "chez-giovanni",
      "note": 4.5,
      "nb_avis": 8,
      "est_favori": true,
      "url": "/restaurants/chez-giovanni/"
    },
    ...
  ],
  "source": "cache"  # ou "calcul"
}
```

#### 2. Enregistrer une interaction implicite

```bash
# POST - Enregistre une vue/clic/partage
curl -X POST https://djib-reco.onrender.com/recommandations/interaction/ \
  -H "Content-Type: application/json" \
  -d '{
    "restaurant_id": 12,
    "type_action": "vue"  # ou "clic_menu", "partage"
  }'

# Réponse réussie
{ "status": "ok" }

# Erreur
{ "erreur": "Données invalides" }  # 400
{ "erreur": "Restaurant introuvable" }  # 404
```

#### 3. Restaurants similaires

```bash
# GET - Retourne 4 restaurants similaires (public - pas d'auth requise)
curl https://djib-reco.onrender.com/recommandations/similaires/chez-giovanni/?nb=4

# Réponse
{
  "similaires": [
    {
      "id": 15,
      "nom": "Marco's Pizza",
      "note": 4.8,
      "est_favori": false,
      ...
    },
    ...
  ]
}
```

---

## Algorithm Details

### Poids des signaux

| Interaction | Poids | Meaning |
|-------------|-------|---------|
| Avis 5⭐   | 5.0   | Signal très fort (note × poids) |
| Avis 4⭐   | 4.0   | Signal fort |
| Avis 3⭐   | 3.0   | Signal moyen |
| Avis 1⭐   | 1.0   | Signal faible |
| Favori ❤️   | 4.0   | Appréciation implicite |
| Vue 👀     | 1.0   | Intérêt basique |
| Clic menu  | 0.5   | Intérêt faible |
| Partage 🔗 | 2.0   | Engagement fort |

Tous les signaux sont **sommés et plafonnés à 10** par utilisateur × restaurant.

### Similarité Cosinus

Deux utilisateurs sont similaires si leurs préférences de restaurants se chevauchent :

$$\text{cosinus}(u1, u2) = \frac{\vec{u1} \cdot \vec{u2}}{||\vec{u1}|| \cdot ||\vec{u2}||}$$

Où chaque vecteur = {restaurant_id: score}

### Cold-start (fallback)

Si un utilisateur a < 3 interactions :
1. On ne peut pas faire du collaborative filtering (pas de voisins)
2. **Fallback** : Top 6 restaurants globaux (Wilson score 95%)
3. Wilson score = score bayésien qui favorise les restaurants avec beaucoup d'avis fiables

---

## Management Command

### Pré-calcul des recommandations

Utile pour réduire la latence API en production :

```bash
# Calcule les recommandations pour tous les utilisateurs
python manage.py precalculer_recommandations

# Force un recalcul même si le cache est frais
python manage.py precalculer_recommandations --force

# Spécifier le nombre de recommandations
python manage.py precalculer_recommandations --nb 10
```

Le résultat est mis en cache pour 1 heure dans `CacheRecommandation`.

---

## Admin Django

Accessible via `/admin/` :

### InteractionUtilisateur
- Liste tous les signaux implicites (vues, clics, partages)
- Filtrable par type d'action et utilisateur
- Indexé (fast queries)

### CacheRecommandation  
- Voir le cache pour chaque utilisateur
- Nombre de recommandations stockées
- Date du dernier calcul

### Signaux (auto)
- Écoute les avis et favoris
- Invalide le cache automatiquement
- Pas à gérer manuellement

---

## Monitoring & Logging

### Logs disponibles

```python
# Dans engine.py
logger.info(f"[Reco] Cold-start pour user {user_id} ({len(profil_cible)} interactions)")
logger.warning(f"[Reco] Impossible d'enregistrer interaction: {e}")

# Dans views.py
logger.error(f"[Reco] Erreur calcul pour user {user.id}: {e}")
```

Configurer Django logging dans `settings.py` pour capturer :

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': { 'class': 'logging.StreamHandler' },
    },
    'loggers': {
        'recommandation': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

---

## Tests

Suite complète de **33 tests** incluant :

```bash
python manage.py test recommandation.tests -v 2
```

### Couverture

- ✅ Moteur (matrice, similarité, algo)
- ✅ Modèles (InteractionUtilisateur, CacheRecommandation)
- ✅ Endpoints API (recommandations, interaction, similaires)
- ✅ Validation des données
- ✅ Gestion des erreurs

---

## Performance

### Optimisations implémentées

1. **Matrice en mémoire** : Construit une matrice utilisateur-restaurant pour accès O(1)
2. **K-neighbors** : Limite à 10 voisins (scalable)
3. **Cache TTL 1h** : Évite les recalculs inutiles
4. **Pré-calcul batch** : Management command pour off-peak
5. **Indexes BD** : Sur (utilisateur, restaurant) et type_action

### Temps de réponse attendus

| Opération | Temps |
|-----------|-------|
| Recommandations (hit cache) | < 50ms |
| Recommandations (calcul) | 200-500ms |
| Similaires (item-based) | 50-100ms |
| Interaction enregistrement | < 10ms |

---

## Intégration Frontend Complète

### 1. Script de base dans `base.html`

```html
{% if user.is_authenticated %}
  <script src="{% static 'js/reco_tracker.js' %}"></script>
{% endif %}
```

### 2. Attributs requis sur les templates

```html
<!-- Détail restaurant -->
<div data-restaurant-id="{{ restaurant.id }}" data-page="detail">...</div>

<!-- Listes -->
<div data-page="liste">
  <div data-restaurant-id="{{ r.id }}">...</div>
</div>

<!-- Accueil avec recommandations -->
<div data-page="accueil">
  <a data-restaurant-id="{{ r.id }}">...</a>
</div>

<!-- Boutons spéciaux -->
<button data-clic-menu data-restaurant-id="{{ r.id }}">Voir</button>
<button data-partage data-restaurant-id="{{ r.id }}">Partager</button>
```

### 3. JavaScript côté client

Le script `reco_tracker.js` gère automatiquement :
- Envoi POST asynchrone (non-bloquant)
- CSRF token extraction
- Error handling silencieux
- Queue de retry (offline support)

---

## Troubleshooting

### "Cold-start" pour tous les utilisateurs
**Problème** : Les recommandations sont toujours le top global  
**Cause** : Pas assez d'interactions enregistrées
**Solution**:
1. Vérifier que `reco_tracker.js` est bien inclus et exécuté
2. Vérifier les network calls dans DevTools (`/recommandations/interaction/`)
3. Vérifier que les utilisateurs sont authentifiés

### Cache ne s'invalide pas après un avis
**Problème** : Voir des recommandations obsolètes
**Cause** : Signal Django non déclenché
**Solution**:
1. Vérifier que `recommandation.apps.RecommandationConfig.ready()` est appelé
2. Vérifier que `INSTALLED_APPS` contient `'recommandation'`
3. Redémarrer Django

### Similarité = 0 pour tous
**Problème** : Aucune recommandation collaboratif
**Cause** : Pas assez de co-rating entre utilisateurs
**Solution**:
1. Augmenter les données de test (seed data)
2. Attendre que plus d'utilisateurs notent les mêmes restaurants

---

## Ressources

- **Code** : [c:\Users\abdou\Documents\GitHub\DjibReco\recommandation\](c:\Users\abdou\Documents\GitHub\DjibReco\recommandation\)
- **Tests** : [recommandation/tests.py](recommandation/tests.py) (33 tests)
- **Frontend** : [static/js/reco_tracker.js](static/js/reco_tracker.js)
- **Admin** : Django admin à `/admin/`

---

**Dernière mise à jour** : 13 avril 2026
