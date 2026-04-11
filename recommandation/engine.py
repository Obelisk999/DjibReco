"""
recommandation/engine.py
Moteur de filtrage collaboratif pour DjibReco.

Algorithme : User-Based Collaborative Filtering avec similarité cosinus.
Sources de signal (scores implicites + explicites) :
  - Avis laissé         → note brute  (1-5)
  - Favori ajouté       → +4.0
  - Vue du restaurant   → +1.0
  - Clic item menu      → +0.5

Cold-start : si l'utilisateur n'a pas encore assez d'historique,
on retombe sur le top global pondéré (Wilson score lower bound).
"""

import math
import logging
from collections import defaultdict

from django.contrib.auth.models import User
from django.db.models import Avg, Count

logger = logging.getLogger(__name__)


# ─── POIDS PAR TYPE D'INTERACTION ────────────────────────────────────────────
POIDS = {
    'avis':      1.0,   # multiplié par la note (1-5) → signal fort
    'favori':    4.0,
    'vue':       1.0,
    'clic_menu': 0.5,
    'partage':   2.0,
}

SEUIL_COLD_START = 3   # nb minimum d'interactions pour CF (sinon fallback)
NB_VOISINS       = 10  # nombre de voisins à considérer
NB_RECO_DEFAULT  = 6   # taille du résultat par défaut


# ─── CONSTRUCTION DE LA MATRICE UTILISATEUR-RESTAURANT ───────────────────────

def construire_matrice():
    """
    Retourne un dict :  {user_id: {restaurant_id: score_agrege}}

    Le score d'un utilisateur pour un restaurant est la somme
    de tous ses signaux sur ce restaurant, plafonnée à 10.
    """
    from restaurants.models import Avis, Favori
    from .models import InteractionUtilisateur

    matrice = defaultdict(lambda: defaultdict(float))

    # 1. Avis explicites (signal le plus fort)
    for avis in Avis.objects.select_related('utilisateur', 'restaurant').iterator():
        score = avis.note * POIDS['avis']  # 1..5
        matrice[avis.utilisateur_id][avis.restaurant_id] += score

    # 2. Favoris
    for fav in Favori.objects.select_related('utilisateur', 'restaurant').iterator():
        matrice[fav.utilisateur_id][fav.restaurant_id] += POIDS['favori']

    # 3. Interactions implicites (vues, clics…)
    for inter in InteractionUtilisateur.objects.iterator():
        poids = POIDS.get(inter.type_action, 0.5)
        matrice[inter.utilisateur_id][inter.restaurant_id] += poids

    # Plafonnement à 10
    for uid in matrice:
        for rid in matrice[uid]:
            matrice[uid][rid] = min(matrice[uid][rid], 10.0)

    return matrice


# ─── SIMILARITÉ COSINUS ───────────────────────────────────────────────────────

def similarite_cosinus(vec_a: dict, vec_b: dict) -> float:
    """
    Calcule la similarité cosinus entre deux vecteurs (dicts rid→score).
    Retourne 0.0 si l'un des vecteurs est vide.
    """
    communs = set(vec_a) & set(vec_b)
    if not communs:
        return 0.0

    dot    = sum(vec_a[r] * vec_b[r] for r in communs)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ─── FILTRAGE COLLABORATIF USER-BASED ────────────────────────────────────────

def recommander_pour_utilisateur(user_id: int, nb: int = NB_RECO_DEFAULT) -> list[int]:
    """
    Retourne une liste ordonnée de restaurant_id recommandés
    pour l'utilisateur `user_id`, sans inclure ceux qu'il a déjà vus/notés.

    Algorithme :
      1. Construire la matrice utilisateur-restaurant
      2. Trouver les NB_VOISINS utilisateurs les plus similaires
      3. Agréger leurs scores pondérés par similarité
      4. Exclure les restaurants déjà connus de l'utilisateur
      5. Trier et retourner les nb premiers
    """
    matrice = construire_matrice()
    profil_cible = matrice.get(user_id, {})

    # Cold-start : pas assez de données
    if len(profil_cible) < SEUIL_COLD_START:
        logger.info(f"[Reco] Cold-start pour user {user_id} ({len(profil_cible)} interactions)")
        return _fallback_top_global(user_id, nb, profil_cible)

    # Calcul des similarités avec tous les autres utilisateurs
    similarites = []
    for uid, profil in matrice.items():
        if uid == user_id:
            continue
        sim = similarite_cosinus(profil_cible, profil)
        if sim > 0:
            similarites.append((uid, sim))

    if not similarites:
        return _fallback_top_global(user_id, nb, profil_cible)

    # Garder les NB_VOISINS meilleurs voisins
    voisins = sorted(similarites, key=lambda x: -x[1])[:NB_VOISINS]

    # Agrégation : score_prédit(restaurant) = Σ(sim_voisin * score_voisin) / Σ(sim_voisin)
    scores_cumules   = defaultdict(float)
    similarites_cumu = defaultdict(float)
    deja_connus      = set(profil_cible.keys())

    for uid_voisin, sim in voisins:
        for rid, score in matrice[uid_voisin].items():
            if rid not in deja_connus:
                scores_cumules[rid]   += sim * score
                similarites_cumu[rid] += sim

    if not scores_cumules:
        return _fallback_top_global(user_id, nb, profil_cible)

    # Score normalisé
    scores_finaux = {
        rid: scores_cumules[rid] / similarites_cumu[rid]
        for rid in scores_cumules
    }

    # Trier et retourner les IDs
    recommandes = sorted(scores_finaux, key=lambda r: -scores_finaux[r])
    return recommandes[:nb]


# ─── RECOMMANDATIONS SIMILAIRES (Item-Based léger) ───────────────────────────

def restaurants_similaires(restaurant_id: int, nb: int = 4) -> list[int]:
    """
    Retourne des restaurants similaires à `restaurant_id` basé sur
    les utilisateurs qui les ont tous les deux appréciés (co-occurrence).
    """
    matrice = construire_matrice()

    # Vecteur du restaurant cible : {user_id: score}
    vec_cible = {uid: scores[restaurant_id]
                 for uid, scores in matrice.items()
                 if restaurant_id in scores}

    if not vec_cible:
        return []

    # Tous les restaurants que ces utilisateurs ont aussi aimés
    candidats = defaultdict(dict)
    for uid in vec_cible:
        for rid, score in matrice[uid].items():
            if rid != restaurant_id:
                candidats[rid][uid] = score

    # Similarité cosinus restaurant_cible ↔ chaque candidat
    scores_sim = {}
    for rid, vec_rid in candidats.items():
        sim = similarite_cosinus(vec_cible, vec_rid)
        if sim > 0:
            scores_sim[rid] = sim

    return sorted(scores_sim, key=lambda r: -scores_sim[r])[:nb]


# ─── FALLBACK : TOP GLOBAL (Wilson score) ────────────────────────────────────

def _fallback_top_global(user_id: int, nb: int, deja_connus: dict) -> list[int]:
    """
    Fallback pour cold-start : retourne les meilleurs restaurants
    selon le Wilson score lower bound (95% confidence).
    Exclut les restaurants déjà connus de l'utilisateur.
    """
    from restaurants.models import Restaurant

    qs = Restaurant.objects.exclude(
        id__in=deja_connus.keys()
    ).annotate(
        note_avg=Avg('avis__note'),
        nb_avis=Count('avis')
    ).filter(est_ouvert=True, nb_avis__gt=0)

    # Wilson score lower bound
    def wilson_score(note_avg, nb_avis):
        if nb_avis == 0:
            return 0
        z = 1.96   # 95%
        p = (note_avg - 1) / 4  # normaliser 1-5 → 0-1
        n = nb_avis
        centre = p + z*z / (2*n)
        marge  = z * math.sqrt(p*(1-p)/n + z*z/(4*n*n))
        denom  = 1 + z*z/n
        return (centre - marge) / denom

    ranked = sorted(
        [(r.id, wilson_score(r.note_avg or 0, r.nb_avis)) for r in qs],
        key=lambda x: -x[1]
    )
    return [rid for rid, _ in ranked[:nb]]


# ─── ENREGISTREMENT D'UNE INTERACTION ────────────────────────────────────────

def enregistrer_interaction(user_id: int, restaurant_id: int, type_action: str) -> None:
    """
    Enregistre une interaction utilisateur de façon asynchrone-safe.
    Peut être appelé depuis n'importe quelle vue Django.
    """
    from .models import InteractionUtilisateur
    try:
        poids = POIDS.get(type_action, 0.5)
        InteractionUtilisateur.objects.create(
            utilisateur_id=user_id,
            restaurant_id=restaurant_id,
            type_action=type_action,
            score=poids,
        )
    except Exception as e:
        logger.warning(f"[Reco] Impossible d'enregistrer interaction: {e}")
