# 🍽️ DjibReco
### *Recommandation de cafés et restaurants à Djibouti propulsée par l'IA*

[![Statut](https://img.shields.io/badge/Statut-En_Développement-yellow?style=flat-square)](.)
[![Stack](https://img.shields.io/badge/Stack-Python_%7C_Django-%23092E20?style=flat-square)](.)
[![Domaine](https://img.shields.io/badge/Domaine-IA_%7C_Systèmes_de_Recommandation-purple?style=flat-square)](.)
[![Licence](https://img.shields.io/badge/Licence-MIT-lightgrey?style=flat-square)](.)

> Comment trouver rapidement à Djibouti un café ou un restaurant qui correspond à ses goûts et à son budget ?
> **DjibReco** répond à cette question grâce à un moteur de recommandation hybride basé sur l'IA.

---

## 🎯 Présentation

**DjibReco** est une application web intelligente qui recommande des cafés et restaurants à Djibouti en combinant deux approches de recommandation dans un modèle hybride — offrant des suggestions personnalisées selon les préférences, les notes et le budget de chaque utilisateur.

---

## 🤖 Système de Recommandation
```
📋 Filtrage par Contenu     👥 Filtrage Collaboratif
──────────────────────      ────────────────────────
Type de cuisine             Notes des utilisateurs
Gamme de prix               Utilisateurs similaires
Tags & localisation         Comportements
```

---

## 🚀 Fonctionnalités

| Fonctionnalité | Statut |
|:---|:---|
| Authentification (inscription / connexion) | 🔄 Prévu |
| Ajout et notation de restaurants | 🔄 Prévu |
| Recommandations personnalisées | 🔄 Prévu |
| Tableau de bord administrateur | 🔄 Prévu |
| Filtrage par budget | 🔄 Prévu |
| Recherche et filtrage de restaurants | 🔄 Prévu |

---

## 🛠️ Stack Technique
```
Backend      →  Python 3 · Django 5.2 · Scikit-learn
Base données →  SQLite (développement) · PostgreSQL (production)
Frontend     →  HTML · CSS · Templates Django
Auth         →  Django Authentication System
```

---

## 📁 Structure du Projet
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

## ⚡ Installation & Lancement

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

## 🔮 Améliorations Futures

- 🌍 Déploiement en ligne
- 📍 Filtrage par géolocalisation
- 📊 Amélioration de l'algorithme de classement
- 👥 Intégration d'un vrai jeu de données utilisateurs
- 💬 Analyse des avis et des sentiments

---

## 📖 Description des Fichiers Clés

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
| `models.py` | Modèles Restaurant, Note |
| `views.py` | Logique des pages |
| `urls.py` | Routes de l'app |

### `accounts/`
Gestion des utilisateurs :

| Fichier | Rôle |
|:---|:---|
| `models.py` | Modèle utilisateur |
| `views.py` | Inscription, connexion |
| `urls.py` | Routes auth |

---

### 🔄 Résumé du Fonctionnement
```
1. manage.py        →  démarre l'application
2. settings.py      →  configure Django
3. urls.py          →  gère le routage
4. models.py        →  gère la structure des données
5. views.py         →  gère la logique des pages
6. templates/       →  gère l'affichage
```

---

## 🤝 Comment Contribuer et Fusionner

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

> ⚠️ **Règle absolue :** Aucun développement direct sur `main`. La branche `main` doit toujours rester stable et fonctionnelle.

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

### 📋 Résumé du Flux de Travail
```
Ta branche (ex: fatouma)
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
