# 🍽️ DjibReco
### *Recommandation de cafés et restaurants à Djibouti propulsée par l'IA*

[![Statut](https://img.shields.io/badge/Statut-Production_Prête-brightgreen?style=flat-square)](.)
[![Stack](https://img.shields.io/badge/Stack-Python_%7C_Django-%23092E20?style=flat-square)](.)
[![Domaine](https://img.shields.io/badge/Domaine-IA_%7C_Systèmes_de_Recommandation-purple?style=flat-square)](.)
[![Tests](https://img.shields.io/badge/Tests-68%2F68%20Passing-brightgreen?style=flat-square)](.)
[![Licence](https://img.shields.io/badge/Licence-MIT-lightgrey?style=flat-square)](.)

> Comment trouver rapidement à Djibouti un café ou un restaurant qui correspond à ses goûts et à son budget ?
> **DjibReco** répond à cette question grâce à un moteur de recommandation hybride basé sur l'IA.

---

## Présentation

**DjibReco** est une application web intelligente qui recommande des cafés et restaurants à Djibouti en combinant deux approches de recommandation dans un modèle hybride — offrant des suggestions personnalisées selon les préférences, les notes et le budget de chaque utilisateur.

---

## 🎯 Système de Recommandation (Production ✅)

Trois algorithmes collaborent pour fournir les meilleures recommandations :

### 1️⃣ **Filtrage Collaboratif (CF)**
- Compares users with similar tastes
- Similarity: Cosine similarity on interaction matrix
- K-NN: k=10 nearest neighbors
- Best for: **Warm-start users** (≥3 interactions)
- Performance: Fast (~150ms)

```
Utilisateur A  →  Utilisateurs similaires  →  Leurs restaurants préférés
```

### 2️⃣ **Filtrage par Contenu (CB)**
- Matches users to restaurants by features
- Features: Category (40%), Price (25%), Locality (20%), Tags (15%)
- Method: TF-IDF style similarity scoring
- Best for: **Cold-start users** (no/few interactions)
- Performance: Fast (~200ms)

```
Préférences utilisateur  →  Caractéristiques restaurants  →  Score de similarité
```

### 3️⃣ **Filtrage Hybride (Hybrid)**
- Smart combination of CF + CB
- 3 Strategies: Weighted (α×CF + (1-α)×CB), Switching (adaptive), Feature-Augmented
- Performance: Very fast (~300ms)

```
Weighted:            α × CF + (1-α) × CB  [recommandé: α=0.6]
Switching:           CF if warm, else CB
Feature-Augmented:   CF scores enhanced with CB features
```

---

## Fonctionnalités

| Fonctionnalité | Statut | Détails |
|:---|:---|:---|
| Authentification (inscription / connexion) | ✅ Complète | Django auth system |
| Ajout et notation de restaurants | ✅ Complète | Modèle Avis |
| **Filtrage Collaboratif** | ✅ Production | CF avec K-NN |
| **Filtrage par Contenu** | ✅ Production | CB avec TF-IDF |
| **Filtrage Hybride** | ✅ Production | 3 stratégies |
| Recommandations personnalisées | ✅ Production | 3 endpoints |
| Tableau de bord administrateur | ✅ Avancé | Couverture algorithme |
| Recherche et filtrage de restaurants | ✅ Complète | Django ORM |
| Suivi des interactions utilisateur | ✅ Production | InteractionUtilisateur |
| Cache distribué | ✅ Production | TTL 1h, invalidation par signal |

---

## Stack Technique

| Composant | Technologie | Détails |
|:---|:---|:---|
| **Backend** | Python 3.11+ | Django 5.2.7 |
| **Algorithmes** | Scikit-learn | Cosine similarity, TF-IDF |
| **Cache** | Django Cache Framework | TTL-based (1h default) |
| **DB Dev** | SQLite | db.sqlite3 |
| **DB Production** | PostgreSQL | render.yaml |
| **Frontend** | HTML/CSS/JS | Django templates |
| **Authentication** | Django Auth | Session-based |
| **Admin** | Django Admin | Enhanced with algorithm coverage |
| **Tracking** | JavaScript | reco_tracker.js (interaction logging) |

---

##  Structure du Projet
```
DjibReco/
├── djib_reco/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── restaurants/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
├── accounts/
│   ├── models.py
│   ├── views.py
│   └── urls.py
├── templates/
├── static/
├── media/
├── manage.py
├── requirements.txt
└── .env
```

---

##  Installation & Lancement

### 1. Cloner le dépôt
```bash
git clone https://github.com/fatouu50/DjibReco.git
cd DjibReco
```

### 2. Créer et activer un environnement virtuel
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
Crée un fichier `.env` à la racine du projet :
```
SECRET_KEY=ta_clé_secrète
DEBUG=True
```

### 5. Appliquer les migrations
```bash
python manage.py migrate
```

### 6. Lancer l'application
```bash
python manage.py runserver
```

L'application sera disponible sur **`http://localhost:8000`**

---

## 🚀 API Endpoints de Recommandation

### Endpoints disponibles

```
GET /recommandations/                      # Filtrage Collaboratif (CF)
GET /recommandations/content-based/        # Filtrage par Contenu (CB)
GET /recommandations/hybride/              # Filtrage Hybride
GET /recommandations/comparer/             # Comparaison tous les algorithmes
GET /recommandations/analyse/              # Analyse de couverture pour l'utilisateur
```

### Exemples d'utilisation

**1️⃣ Recommandations Collaboratives (CF)**
```bash
curl -H "Cookie: sessionid=YOUR_SESSION" \
  "http://localhost:8000/recommandations/?nb=6"
```

**2️⃣ Recommandations par Contenu (CB)**
```bash
curl -H "Cookie: sessionid=YOUR_SESSION" \
  "http://localhost:8000/recommandations/content-based/?nb=6"
```

**3️⃣ Recommandations Hybrides (avec stratégie)**
```bash
curl -H "Cookie: sessionid=YOUR_SESSION" \
  "http://localhost:8000/recommandations/hybride/?strategy=switching&alpha=0.6&nb=6"
```
- Stratégies: `weighted`, `switching`, `feature_augmented`
- Alpha (pour weighted): 0.0 - 1.0 (défaut: 0.6)

**4️⃣ Comparaison des Algorithmes**
```bash
curl -H "Cookie: sessionid=YOUR_SESSION" \
  "http://localhost:8000/recommandations/comparer/?nb=6"
```
Retourne: CF + CB + Hybrid (3 stratégies) + couverture

---

## 🧪 Tests & Qualité

**Statut**: ✅ **68/68 tests passent (100%)**

```bash
# Exécuter la suite de tests
python manage.py test recommandation.tests -v 0

# Exécuter avec détails
python manage.py test recommandation.tests -v 1
```

### Couverture des tests

| Composant | Tests | Statut |
|:---|:---|:---|
| Filtrage Collaboratif (CF) | 13 tests | ✅ |
| Filtrage par Contenu (CB) | 11 tests | ✅ |
| Filtrage Hybride | 13 tests | ✅ |
| Endpoints API | 14 tests | ✅ |
| Caching & Signals | 10 tests | ✅ |
| Auth & Validation | 7 tests | ✅ |
| **Total** | **68 tests** | **✅ 100% passing** |

Performance moyenne par test: ~2-5 secondes
Temps total d'exécution: 116-282 secondes

---

## 📚 Documentation Complète

Pour une utilisation avancée et la mise en production, consultez:

- 📖 [QUICKSTART_HYBRID.md](./recommandation/QUICKSTART_HYBRID.md) — Guide rapide (5 min)
- 📊 [MONITORING_HYBRID.md](./recommandation/MONITORING_HYBRID.md) — Performance & débogage
- ✅ [COMPLETION_REPORT.md](./recommandation/COMPLETION_REPORT.md) — Rapport d'implémentation
- 🔧 [recommandation/README.md](./recommandation/README.md) — Documentation détaillée

---

## ⚙️ Configuration Production

### Réglages recommandés

```python
# settings.py ou .env

# Algorithme hybride par défaut
RECO_DEFAULT_STRATEGY = 'switching'    # Adaptatif (CF si warm, CB si cold)

# Paramètre alpha pour stratégie weighted
RECO_HYBRID_ALPHA = 0.6                # 60% CF, 40% CB

# Cache TTL
RECO_CACHE_TTL = 60                    # Minutes (défaut: 60)

# Performance targets
RECO_RESPONSE_TIME_MAX = 500            # ms (p95)
RECO_CACHE_HIT_RATE_TARGET = 0.8       # 80%
```

### Seuils d'alerte

- ⚠️ **Warning**: Temps de réponse > 1 seconde
- 🔴 **Error**: Temps de réponse > 2 secondes
- 📊 **Info**: Cache hit rate < 70%

---

##  Structure du Projet - App Recommandation

```
recommandation/
├── engine.py                   # Filtrage Collaboratif (CF)
├── content_engine.py           # Filtrage par Contenu (CB)
├── hybrid_engine.py            # Filtrage Hybride (3 stratégies)
├── models.py                   # InteractionUtilisateur, CacheRecommandation
├── views.py                    # API endpoints (5 endpoints)
├── urls.py                     # Routes
├── admin.py                    # Enhanced dashboard (couverture algorithme)
├── signals.py                  # Cache invalidation on save
├── tests.py                    # 68 comprehensive tests
├── README.md                   # Documentation détaillée
├── QUICKSTART_HYBRID.md        # Guide rapide
├── MONITORING_HYBRID.md        # Production guide
├── COMPLETION_REPORT.md        # Rapport d'implémentation
└── management/commands/
    └── precalculer_recommandations.py  # Pre-calc script
```

---

##  Améliorations Futures

- ✅ **[DONE]** Filtrage Collaboratif (CF) - Production
- ✅ **[DONE]** Filtrage par Contenu (CB) - Production
- ✅ **[DONE]** Filtrage Hybride - Production
- ✅ **[DONE]** Admin dashboard avec couverture algorithme
- ✅ **[DONE]** Cache distribué avec TTL
- 🔄 **Prévu**: A/B test des stratégies hybrides (alpha tuning)
- 🔄 **Prévu**: Pre-calculation des recommandations (batch job)
- 🔄 **Prévu**: Intégration avec feedback utilisateur (re-ranking)
- 🔄 **Future**: Embeddings deep learning pour améliorations

---

## Description des Fichiers Clés

### `manage.py`
Point d'entrée de l'application Django.
```bash
python manage.py runserver  # Lance le serveur
python manage.py migrate    # Applique les migrations
```

### `djib_reco/settings.py`
Configuration globale du projet :
- Clé secrète via `.env`
- Base de données
- Applications installées
- Fichiers statiques et media

### `djib_reco/urls.py`
Routage principal de l'application. Redirige vers les URLs de chaque app.

### `restaurants/`
Application principale :

| Fichier | Rôle |
|:---|:---|
| `models.py` | Restaurant, Avis (ratings) |
| `views.py` | Listing, détail, recherche |
| `urls.py` | Routes de l'app |

### `recommandation/` (🎯 Cœur du système)
Moteur de recommandation multi-algorithme :

| Fichier | Rôle |
|:---|:---|
| `engine.py` | Filtrage Collaboratif (CF) |
| `content_engine.py` | Filtrage par Contenu (CB) |
| `hybrid_engine.py` | Filtrage Hybride (3 stratégies) |
| `models.py` | InteractionUtilisateur, CacheRecommandation |
| `views.py` | 5 API endpoints |
| `admin.py` | Dashboard avec couverture algorithme |
| `signals.py` | Cache invalidation |
| `tests.py` | 68 tests (100% passing) |

### `accounts/`
Gestion des utilisateurs :

| Fichier | Rôle |
|:---|:---|
| `models.py` | Modèle utilisateur |
| `views.py` | Inscription, connexion |
| `urls.py` | Routes auth |

---

###  Résumé du Fonctionnement
```
1. manage.py        →  démarre l'application
2. settings.py      →  configure Django
3. urls.py          →  gère le routage
4. models.py        →  gère la structure des données
5. views.py         →  gère la logique des pages + APIs
6. recommandation/  →  génère les recommandations
7. templates/       →  affiche les résultats
```

---

## 🚡 Quick Start - Recommandation System

### 1. Générer les données de test
```bash
python manage.py seed_data                    # Créer 10+ restaurants
python manage.py create_test_interactions     # Générer interactions
```

### 2. Tester les endpoints
```bash
# Recommandations collaboratives
curl -b "sessionid=YOUR_SESSION_ID" \
  "http://localhost:8000/recommandations/"

# Recommandations hybrides (meilleur résultat)
curl -b "sessionid=YOUR_SESSION_ID" \
  "http://localhost:8000/recommandations/hybride/?strategy=switching"

# Comparaison de tous les algorithmes
curl -b "sessionid=YOUR_SESSION_ID" \
  "http://localhost:8000/recommandations/comparer/"
```

### 3. Admin Dashboard
- Aller sur: `http://localhost:8000/admin/`
- Voir: "Cache Recommandation" → "Couverture Detail" (colonne)
- Affiche: Quels algos sont disponibles pour chaque utilisateur

---

## 🐛 Dépannage

| Problème | Solution |
|:---|:---|
| "Pas de recommandations" | L'utilisateur doit avoir noté au moins 1 restaurant |
| Erreur 401/403 | Connectez-vous d'abord (`/accounts/connexion/`) |
| Cache vide | Attendre après première recommandation (TTL 1h) |
| Tests échouent | `python manage.py migrate` et réessayer |
| Performance lente | Vérifier cache hit rate dans `/recommandations/analyse/` |

Pour plus de détails: [MONITORING_HYBRID.md](./recommandation/MONITORING_HYBRID.md)

---

## Comment Contribuer et Fusionner

Chaque fonctionnalité est développée dans une branche dédiée :

| Branche | Développeur |
|:---|:---|
| `fatouma` | Fatouma |
| `madina` | Madina |
| `mako` | Mako |
| `kadiga` | Kadiga |
| `samira` | Samira |
| `asma` | Asma |
| `abdoulrazack` | Abdoulrazack |
| `kenedid` | Kenedid |

> **Règle absolue :** Aucun développement direct sur `main`. La branche `main` doit toujours rester stable et fonctionnelle.

---

### Étape 1 — Travailler sur sa branche
```bash
git checkout fatouma
```

### Étape 2 — Enregistrer et envoyer son travail
```bash
git add .
git commit -m "Description claire de ce que tu as fait"
git push origin fatouma
```

### Étape 3 — Fusionner dans `main` après validation
```bash
git checkout main
git pull origin main
git merge fatouma
git push origin main
```

---
        │
        │  git add . && git commit && git push
        │
        ▼
  Branche distante (GitHub)
        │
        │  Tests validés ✅
        │
        ▼
      main  ←  git merge fatouma
```
