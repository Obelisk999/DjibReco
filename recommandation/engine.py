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
import time
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
    Construit la matrice utilisateur-restaurant avec tous les signaux agrégés.
    
    Retourne un dict : {user_id: {restaurant_id: score_agrege}}
    
    Processus:
      1. Parcourir tous les avis → score = note × 1.0 (signal 1-5)
      2. Parcourir tous les favoris → ajouter 4.0 par favori
      3. Parcourir toutes les interactions implicites → ajouter poids spécifique
      4. Plafonner chaque score à 10.0 (max pertinent)
    
    Complexité: O(n) où n = total interactions
    """
    from restaurants.models import Avis, Favori
    from .models import InteractionUtilisateur

    start = time.time()
    matrice = defaultdict(lambda: defaultdict(float))

    # 1. Avis explicites (signal le plus fort)
    avis_count = 0
    for avis in Avis.objects.select_related('utilisateur', 'restaurant').iterator():
        score = avis.note * POIDS['avis']  # 1..5
        matrice[avis.utilisateur_id][avis.restaurant_id] += score
        avis_count += 1

    # 2. Favoris
    fav_count = 0
    for fav in Favori.objects.select_related('utilisateur', 'restaurant').iterator():
        matrice[fav.utilisateur_id][fav.restaurant_id] += POIDS['favori']
        fav_count += 1

    # 3. Interactions implicites (vues, clics…)
    inter_count = 0
    for inter in InteractionUtilisateur.objects.iterator():
        poids = POIDS.get(inter.type_action, 0.5)
        matrice[inter.utilisateur_id][inter.restaurant_id] += poids
        inter_count += 1

    # Plafonnement à 10
    for uid in matrice:
        for rid in matrice[uid]:
            matrice[uid][rid] = min(matrice[uid][rid], 10.0)

    elapsed = time.time() - start
    logger.info(
        f'[MatriceConstruction] {len(matrice)} users, '
        f'{avis_count} avis, {fav_count} favoris, {inter_count} interactions '
        f'(temps: {elapsed:.2f}s)'
    )
    
    return matrice


# ─── SIMILARITÉ COSINUS ───────────────────────────────────────────────────────

def similarite_cosinus(vec_a: dict, vec_b: dict) -> float:
    """
    Calcule la similarité cosinus entre deux vecteurs.
    
    La similarité cosinus mesure l'angle entre deux vecteurs:
      - 1.0 = vecteurs identiques (préférences identiques)
      - 0.5 = préférences partiellement alignées
      - 0.0 = aucun chevauchement ou un vecteur vide
      
    Args:
        vec_a, vec_b: dicts {restaurant_id: score}
        
    Retourne:
        float entre 0.0 et 1.0
        
    Formule:
        cosinus(a, b) = (a·b) / (||a|| × ||b||)
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
    Recommande des restaurants pour un utilisateur via filtrage collaboratif.
    
    Algorithme : User-Based Collaborative Filtering avec similarité cosinus
    
    Étapes:
      1. Construire la matrice d'interactions (all users × all restaurants)
      2. Si l'utilisateur a < SEUIL_COLD_START interactions → fallback Wilson
      3. Calculer similarité cosinus vs tous les autres utilisateurs
      4. Conserver les K_NEIGHBORS=10 utilisateurs les plus similaires
      5. Agréger leurs scores pondérés par similarité
      6. Exclure restaurants déjà connus de l'utilisateur
      7. Retourner les nb restaurants avec les meilleurs scores
      
    Paramètres:
        user_id: ID de l'utilisateur cible
        nb: Nombre max de recommandations (défaut: 6)
        
    Retourne:
        list[int]: IDs de restaurants recommandés, ordonnés par score décroissant
        
    Cas limites:
        - User inconnu → fallback global
        - User n'a aucun voisin → fallback global
        - Tous les restaurants déjà notés → [] vide
    """
    start = time.time()
    matrice = construire_matrice()
    profil_cible = matrice.get(user_id, {})

    # Cold-start : pas assez de données
    if len(profil_cible) < SEUIL_COLD_START:
        logger.info(
            f'[RecoMotor] Cold-start pour user {user_id} '
            f'({len(profil_cible)} interactions < {SEUIL_COLD_START})'
        )
        result = _fallback_top_global(user_id, nb, profil_cible)
        elapsed = time.time() - start
        logger.info(f'[RecoMotor] Cold-start retourné {len(result)} resultats en {elapsed:.3f}s')
        return result

    # Calcul des similarités avec tous les autres utilisateurs
    similarites = []
    for uid, profil in matrice.items():
        if uid == user_id:
            continue
        sim = similarite_cosinus(profil_cible, profil)
        if sim > 0:
            similarites.append((uid, sim))

    if not similarites:
        logger.warning(f'[RecoMotor] Aucun voisin similaire pour user {user_id}')
        result = _fallback_top_global(user_id, nb, profil_cible)
        return result

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
        logger.info(f'[RecoMotor] Aucun restaurant non-connu pour user {user_id}')
        result = []
    else:
        # Score normalisé
        scores_finaux = {
            rid: scores_cumules[rid] / similarites_cumu[rid]
            for rid in scores_cumules
        }

        # Trier et retourner les IDs
        recommandes = sorted(scores_finaux, key=lambda r: -scores_finaux[r])
        result = recommandes[:nb]

    elapsed = time.time() - start
    logger.info(
        f'[RecoMotor] User {user_id}: {len(voisins)} voisins, '
        f'{len(result)} recommendations (temps: {elapsed:.3f}s)'
    )
    
    return result


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
    
    Args:
        user_id: ID utilisateur
        restaurant_id: ID restaurant
        type_action: 'vue', 'clic_menu', 'partage'
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
        logger.debug(
            f'[Interaction] user {user_id} → resto {restaurant_id} [{type_action}]'
        )
    except Exception as e:
        logger.warning(f"[Interaction] Impossible d'enregistrer: {e}")
