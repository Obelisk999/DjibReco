"""
recommandation/views.py
Endpoints Django pour le système de recommandation.

  GET  /recommandations/pour-moi/          → liste JSON des restaurants recommandés
  POST /recommandations/interaction/       → enregistre une interaction implicite
  GET  /recommandations/similaires/<slug>/ → restaurants similaires (item-based)

Format des logs:
  [RecoAPI] <operation> <user_id> - <details> (<timing>)
"""
import json
import logging
import time
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from restaurants.models import Restaurant
from .engine import (
    recommander_pour_utilisateur,
    restaurants_similaires,
    enregistrer_interaction,
)
from .content_engine import recommander_content_based
from .hybrid_engine import recommander_hybride, comparer_recommandations, analyser_couverture_algorithme
from .models import CacheRecommandation

logger = logging.getLogger(__name__)

CACHE_TTL_MINUTES = 60   # durée de validité du cache


def _restaurant_to_dict(r: Restaurant, favoris_ids: set) -> dict:
    """Sérialise un Restaurant pour la réponse JSON."""
    return {
        'id':          r.id,
        'nom':         r.nom,
        'slug':        r.slug,
        'adresse':     r.adresse,
        'gamme_prix':  r.gamme_prix,
        'horaires':    r.horaires,
        'categorie':   r.categorie.nom if r.categorie else '',
        'note':        r.note_moyenne(),
        'nb_avis':     r.nombre_avis(),
        'image':       r.get_image() or '',
        'est_favori':  r.id in favoris_ids,
        'url':         f'/restaurants/{r.slug}/',
    }


# ─── RECOMMANDATIONS PERSONNALISÉES ──────────────────────────────────────────

@login_required
@require_GET
def recommandations_pour_moi(request):
    """
    Retourne jusqu'à 6 restaurants recommandés pour l'utilisateur connecté.
    Utilise le cache si disponible et frais (< CACHE_TTL_MINUTES).
    """
    start = time.time()
    user = request.user
    nb   = int(request.GET.get('nb', 6))
    
    logger.info(f'[RecoAPI:recommandations] Début pour user {user.id} (nb={nb})')

    # Vérifier le cache
    cache_hit = False
    try:
        cache = CacheRecommandation.objects.get(utilisateur=user)
        age   = timezone.now() - cache.calculee_le
        if age < timedelta(minutes=CACHE_TTL_MINUTES) and cache.restaurant_ids:
            ids_caches = cache.restaurant_ids[:nb]
            restaurants = _charger_restaurants(ids_caches, user)
            elapsed = time.time() - start
            logger.info(
                f'[RecoAPI:recommandations] Cache HIT {len(restaurants)} '
                f'resultats ({elapsed:.3f}s)'
            )
            return JsonResponse({'recommandations': restaurants, 'source': 'cache'})
    except CacheRecommandation.DoesNotExist:
        pass

    # Calculer les recommandations
    try:
        ids = recommander_pour_utilisateur(user.id, nb=nb)
    except Exception as e:
        elapsed = time.time() - start
        logger.error(
            f'[RecoAPI:recommandations] ERREUR user {user.id}: {e} ({elapsed:.3f}s)'
        )
        return JsonResponse({'erreur': 'Calcul indisponible'}, status=500)

    # Mettre en cache
    CacheRecommandation.objects.update_or_create(
        utilisateur=user,
        defaults={'restaurant_ids': ids}
    )

    restaurants = _charger_restaurants(ids, user)
    elapsed = time.time() - start
    logger.info(
        f'[RecoAPI:recommandations] Calcul {len(restaurants)} resultats ({elapsed:.3f}s)'
    )
    
    return JsonResponse({'recommandations': restaurants, 'source': 'calcul'})


def _charger_restaurants(ids: list, user) -> list:
    """Charge les restaurants depuis les IDs et les sérialise."""
    from restaurants.models import Favori
    favoris_ids = set(
        Favori.objects.filter(utilisateur=user).values_list('restaurant_id', flat=True)
    )
    # Garder l'ordre de la liste d'IDs
    qs    = Restaurant.objects.filter(id__in=ids, est_ouvert=True).select_related('categorie')
    index = {r.id: r for r in qs}
    return [
        _restaurant_to_dict(index[rid], favoris_ids)
        for rid in ids
        if rid in index
    ]


# ─── ENREGISTREMENT D'INTERACTION IMPLICITE ───────────────────────────────────

@login_required
@require_POST
def enregistrer_interaction_view(request):
    """
    Endpoint AJAX pour enregistrer une interaction implicite.
    Body JSON : {"restaurant_id": 12, "type_action": "vue"}
    """
    start = time.time()
    
    try:
        data        = json.loads(request.body)
        rid         = int(data['restaurant_id'])
        type_action = data['type_action']
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        logger.warning(
            f'[RecoAPI:interaction] Données invalides user {request.user.id}: {e}'
        )
        return JsonResponse({'erreur': 'Données invalides'}, status=400)

    types_valides = {'vue', 'clic_menu', 'partage'}
    if type_action not in types_valides:
        logger.warning(
            f'[RecoAPI:interaction] Type invalide {type_action} user {request.user.id}'
        )
        return JsonResponse({'erreur': f'type_action doit être parmi {types_valides}'}, status=400)

    if not Restaurant.objects.filter(id=rid).exists():
        logger.warning(
            f'[RecoAPI:interaction] Resto {rid} inexistant user {request.user.id}'
        )
        return JsonResponse({'erreur': 'Restaurant introuvable'}, status=404)

    enregistrer_interaction(request.user.id, rid, type_action)
    elapsed = time.time() - start
    logger.info(
        f'[RecoAPI:interaction] user {request.user.id} → '
        f'resto {rid} [{type_action}] ({elapsed:.3f}s)'
    )
    
    return JsonResponse({'status': 'ok'})


# ─── RESTAURANTS SIMILAIRES (widget sur page détail) ─────────────────────────

@require_GET
def restaurants_similaires_view(request, slug):
    """
    Retourne jusqu'à 4 restaurants similaires à celui identifié par `slug`.
    Accessible sans connexion (résultat non personnalisé).
    """
    start = time.time()
    
    restaurant = get_object_or_404(Restaurant, slug=slug)
    nb         = int(request.GET.get('nb', 4))
    
    logger.info(f'[RecoAPI:similaires] Début pour resto {restaurant.id} (nb={nb})')

    ids = restaurants_similaires(restaurant.id, nb=nb)

    favoris_ids = set()
    if request.user.is_authenticated:
        from restaurants.models import Favori
        favoris_ids = set(
            Favori.objects.filter(utilisateur=request.user).values_list('restaurant_id', flat=True)
        )

    restaurants = _charger_restaurants(ids, request.user) if request.user.is_authenticated \
                  else _charger_restaurants_anon(ids)

    elapsed = time.time() - start
    logger.info(
        f'[RecoAPI:similaires] Retourné {len(restaurants)} resultats ({elapsed:.3f}s)'
    )
    
    return JsonResponse({'similaires': restaurants})


def _charger_restaurants_anon(ids: list) -> list:
    qs    = Restaurant.objects.filter(id__in=ids, est_ouvert=True).select_related('categorie')
    index = {r.id: r for r in qs}
    return [_restaurant_to_dict(index[rid], set()) for rid in ids if rid in index]


# ─── RECOMMANDATIONS CONTENT-BASED ─────────────────────────────────────────

@login_required
@require_GET
def recommandations_content_based(request):
    """
    Retourne jusqu'à 6 restaurants recommandés via Content-Based Filtering.
    Basé sur les caractéristiques des restaurants que l'utilisateur a aimés.
    """
    start = time.time()
    user = request.user
    nb   = int(request.GET.get('nb', 6))
    
    logger.info(f'[RecoAPI:content-based] Début pour user {user.id} (nb={nb})')

    try:
        recs = recommander_content_based(user.id, nb=nb)
        ids = [r_id for r_id, _ in recs]  # Décompile les tuples (id, score)
    except Exception as e:
        elapsed = time.time() - start
        logger.error(
            f'[RecoAPI:content-based] ERREUR user {user.id}: {e} ({elapsed:.3f}s)'
        )
        return JsonResponse({'erreur': 'Calcul indisponible'}, status=500)

    restaurants = _charger_restaurants(ids, user)
    elapsed = time.time() - start
    logger.info(
        f'[RecoAPI:content-based] Retourné {len(restaurants)} resultats ({elapsed:.3f}s)'
    )
    
    return JsonResponse({'recommandations': restaurants, 'methode': 'content-based'})


# ─── RECOMMANDATIONS HYBRIDES ─────────────────────────────────────────────

@login_required
@require_GET
def recommandations_hybride(request):
    """
    Retourne jusqu'à 6 restaurants via recommandations hybrides.
    Combine Collaborative Filtering et Content-Based Filtering.
    
    Stratégies disponibles:
      - weighted (défaut): α*CF + (1-α)*CB
      - switching: CF si assez d'interactions, sinon CB
      - feature_augmented: CF amélioré avec features CB
    """
    start = time.time()
    user = request.user
    nb       = int(request.GET.get('nb', 6))
    alpha    = float(request.GET.get('alpha', 0.6))
    strategy = request.GET.get('strategy', 'weighted')
    
    # Valider la stratégie
    strategies_valides = {'weighted', 'switching', 'feature_augmented'}
    if strategy not in strategies_valides:
        logger.warning(
            f'[RecoAPI:hybride] Stratégie invalide {strategy} user {user.id}'
        )
        return JsonResponse(
            {'erreur': f'strategy doit être parmi {strategies_valides}'},
            status=400
        )
    
    logger.info(
        f'[RecoAPI:hybride] Début user {user.id} '
        f'(nb={nb}, alpha={alpha}, strategy={strategy})'
    )

    try:
        ids = recommander_hybride(user.id, nb=nb, alpha=alpha, strategy=strategy)
    except Exception as e:
        elapsed = time.time() - start
        logger.error(
            f'[RecoAPI:hybride] ERREUR user {user.id}: {e} ({elapsed:.3f}s)'
        )
        return JsonResponse({'erreur': 'Calcul indisponible'}, status=500)

    restaurants = _charger_restaurants(ids, user)
    elapsed = time.time() - start
    logger.info(
        f'[RecoAPI:hybride] Retourné {len(restaurants)} resultats '
        f'({elapsed:.3f}s, strategy={strategy})'
    )
    
    return JsonResponse({
        'recommandations': restaurants,
        'methode': 'hybride',
        'strategy': strategy,
        'alpha': alpha
    })


# ─── COMPARAISON D'ALGORITHMES (DEBUG/TESTING) ──────────────────────────────

@login_required
@require_GET
def comparer_algorithmes(request):
    """
    Compare tous les algorithmes pour un utilisateur.
    Utile pour le debug et A/B testing.
    """
    start = time.time()
    user = request.user
    nb   = int(request.GET.get('nb', 6))
    
    logger.info(f'[RecoAPI:comparer] Début pour user {user.id}')

    try:
        resultats = comparer_recommandations(user.id, nb=nb)
    except Exception as e:
        elapsed = time.time() - start
        logger.error(
            f'[RecoAPI:comparer] ERREUR user {user.id}: {e} ({elapsed:.3f}s)'
        )
        return JsonResponse({'erreur': 'Calcul indisponible'}, status=500)

    # Séparer la couverture du reste
    coverage = resultats.pop('coverage')
    
    # Convertir les IDs en objets Restaurant
    for key in ['cf', 'cb', 'hybrid_weighted', 'hybrid_switching', 'hybrid_augmented']:
        ids = resultats[key]  # Maintenant une liste d'IDs, pas des tuples
        resultats[key] = _charger_restaurants(ids, user)

    elapsed = time.time() - start
    logger.info(f'[RecoAPI:comparer] Comparaison complète ({elapsed:.3f}s)')
    
    return JsonResponse({
        'comparaison': resultats,
        'user_coverage': coverage
    })


# ─── ANALYSE DE COUVERTURE UTILISATEUR ──────────────────────────────────────

@login_required
@require_GET
def analyse_utilisateur(request):
    """
    Analyse la couverture algorithmique pour l'utilisateur.
    Indique quels algorithmes peuvent être utilisés et pourquoi.
    """
    start = time.time()
    user = request.user
    
    logger.info(f'[RecoAPI:analyse] Analyse user {user.id}')

    try:
        couverture = analyser_couverture_algorithme(user.id)
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f'[RecoAPI:analyse] ERREUR user {user.id}: {e} ({elapsed:.3f}s)')
        return JsonResponse({'erreur': 'Analyse indisponible'}, status=500)

    elapsed = time.time() - start
    logger.info(f'[RecoAPI:analyse] Analyse complète ({elapsed:.3f}s)')
    
    return JsonResponse({'couverture': couverture})

