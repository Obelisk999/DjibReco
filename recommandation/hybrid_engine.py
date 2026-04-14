"""
Hybrid Filtering Engine for Restaurant Recommendations

Combines User-Based Collaborative Filtering and Content-Based Filtering
to provide robust recommendations across different user scenarios.

Fusion Strategies:
  1. Weighted Average: α*CF_score + (1-α)*CB_score (default α=0.6)
  2. Algorithm Switching: Use CF if user has 3+ interactions, else CB
  3. Feature Augmented: Enhance CF scores with CB features
  
Default Configuration:
  - Alpha: 0.6 (weighted toward collaborative filtering)
  - Cold-start threshold: 3 interactions
  - Cold-start algorithm: Content-Based Filtering
"""

import logging
import time
from django.db.models import Count

logger = logging.getLogger(__name__)


def recommander_hybride(user_id, nb=6, alpha=0.6, strategy='weighted'):
    """
    Generate hybrid recommendations combining CF and CB approaches.
    
    Args:
        user_id: Django User ID
        nb: Number of recommendations to return (default 6)
        alpha: Weight for CF vs CB (0.6 = 60% CF, 40% CB) - only for 'weighted' strategy
        strategy: Fusion strategy - 'weighted', 'switching', or 'feature_augmented'
        
    Returns:
        list: Restaurant IDs sorted by hybrid score
              [resto_id, resto_id, ...]
    """
    try:
        start = time.time()
        
        from recommandation.engine import recommander_pour_utilisateur
        from recommandation.content_engine import recommander_content_based
        from recommandation.models import InteractionUtilisateur
        
        # Get user interaction count for cold-start detection
        interaction_count = InteractionUtilisateur.objects.filter(
            utilisateur_id=user_id
        ).count()
        
        # Choose strategy based on user interaction history
        if strategy == 'switching':
            if interaction_count < 3:
                # Use content-based for cold-start
                logger.info(f'[HybridEngine:Recommander] user {user_id} cold-start (CB mode)')
                recs = recommander_content_based(user_id, nb)
                result = [r_id for r_id, _ in recs]
                elapsed = time.time() - start
                logger.info(f'[HybridEngine:Recommander] {len(result)} recommendations en {elapsed:.3f}s (switching→CB)')
                return result
            else:
                # Use collaborative filtering for warm users
                logger.info(f'[HybridEngine:Recommander] user {user_id} warm user (CF mode)')
                recs = recommander_pour_utilisateur(user_id, nb)
                elapsed = time.time() - start
                logger.info(f'[HybridEngine:Recommander] {len(recs)} recommendations en {elapsed:.3f}s (switching→CF)')
                return recs
        
        elif strategy == 'feature_augmented':
            # Get CF recommendations (list of IDs)
            cf_recs_ids = recommander_pour_utilisateur(user_id, nb * 2)
            if not cf_recs_ids:
                # Fallback to content-based
                recs = recommander_content_based(user_id, nb)
                elapsed = time.time() - start
                logger.info(f'[HybridEngine:Recommander] {len(recs)} recommendations en {elapsed:.3f}s (feature_augmented→CB fallback)')
                return [r_id for r_id, _ in recs]
            
            # Enhance with content-based features
            enhanced_recs = []
            from recommandation.content_engine import (
                extraire_features_restaurant,
                construire_profil_utilisateur,
                similarite_contenu
            )
            from restaurants.models import Restaurant
            
            user_profil = construire_profil_utilisateur(user_id)
            
            for resto_id in cf_recs_ids:
                try:
                    restaurant = Restaurant.objects.get(id=resto_id)
                    features = extraire_features_restaurant(restaurant)
                    
                    # Calculate content similarity
                    cb_score = similarite_contenu(user_profil, features)
                    
                    # We need CF score, but we only have IDs. Use position as proxy.
                    cf_score = 1.0 / (cf_recs_ids.index(resto_id) + 1)
                    
                    # Blend scores with feature augmentation
                    augmented_score = (alpha * cf_score) + ((1 - alpha) * cb_score)
                    enhanced_recs.append((resto_id, augmented_score))
                except Restaurant.DoesNotExist:
                    continue
            
            enhanced_recs.sort(key=lambda x: x[1], reverse=True)
            result = [r_id for r_id, _ in enhanced_recs[:nb]]
            
            elapsed = time.time() - start
            logger.info(f'[HybridEngine:Recommander] {len(result)} recommendations en {elapsed:.3f}s (feature_augmented)')
            return result
        
        else:  # 'weighted' (default)
            # Get both CF and CB recommendations
            cf_recs_ids = recommander_pour_utilisateur(user_id, nb * 2)
            # cb_recs returns [(id, score), ...]
            cb_recs_tuples = recommander_content_based(user_id, nb * 2)
            
            # Normalize scores to 0-1 range
            cf_dict = {}
            cb_dict = {}
            
            if cf_recs_ids:
                # CF returns list of IDs, use position as score
                for i, resto_id in enumerate(cf_recs_ids):
                    cf_dict[resto_id] = 1.0 / (i + 1)
                max_cf = max(cf_dict.values()) if cf_dict else 1.0
                cf_dict = {k: v / max(max_cf, 0.001) for k, v in cf_dict.items()}
            
            if cb_recs_tuples:
                cb_dict = {resto_id: score for resto_id, score in cb_recs_tuples}
                max_cb = max([score for _, score in cb_recs_tuples]) if cb_recs_tuples else 1.0
                cb_dict = {k: v / max(max_cb, 0.001) for k, v in cb_dict.items()}
            
            # Fuse recommendations
            all_resto_ids = set(cf_dict.keys()) | set(cb_dict.keys())
            hybrid_scores = []
            
            for resto_id in all_resto_ids:
                cf_score = cf_dict.get(resto_id, 0.0)
                cb_score = cb_dict.get(resto_id, 0.0)
                
                # Weighted combination
                hybrid_score = (alpha * cf_score) + ((1 - alpha) * cb_score)
                hybrid_scores.append((resto_id, hybrid_score))
            
            # Sort and limit
            hybrid_scores.sort(key=lambda x: x[1], reverse=True)
            result = [r_id for r_id, _ in hybrid_scores[:nb]]
            
            elapsed = time.time() - start
            logger.info(f'[HybridEngine:Recommander] {len(result)} recommendations en {elapsed:.3f}s (weighted α={alpha})')
            return result
        
    except Exception as e:
        logger.error(f'[HybridEngine:Recommander] Erreur user {user_id}: {str(e)}')
        # Fallback to content-based
        try:
            from recommandation.content_engine import recommander_content_based
            recs = recommander_content_based(user_id, nb)
            return [r_id for r_id, _ in recs]
        except Exception as e:
            logger.warning(f'[HybridEngine] Fallback CB failed for user {user_id}: {str(e)}')
            return []


def analyser_couverture_algorithme(user_id):
    """
    Analyze which algorithms can serve a specific user.
    
    Determines algorithm availability based on user's interaction history.
    Useful for debugging and monitoring which users might benefit from different approaches.
    
    Args:
        user_id: Django User ID
        
    Returns:
        dict: Algorithm coverage analysis
        {
            'used_cf': bool,
            'used_cb': bool,
            'interaction_count': int,
            'cold_start': bool,
            'recommendation_status': str
        }
    """
    try:
        from recommandation.models import InteractionUtilisateur
        from restaurants.models import Avis
        
        interaction_count = InteractionUtilisateur.objects.filter(
            utilisateur_id=user_id
        ).count()
        
        avis_count = Avis.objects.filter(
            utilisateur_id=user_id
        ).count()
        
        is_cold_start = interaction_count < 3 and avis_count < 2
        
        return {
            'used_cf': interaction_count >= 3 and avis_count >= 1,
            'used_cb': avis_count >= 1,
            'interaction_count': interaction_count,
            'avis_count': avis_count,
            'cold_start': is_cold_start,
            'recommendation_status': (
                'cold_start' if is_cold_start
                else 'warm_cf' if interaction_count >= 3
                else 'warm_cb'
            )
        }
        
    except Exception as e:
        logger.error(f'[HybridEngine:Couverture] Erreur user {user_id}: {str(e)}')
        return {
            'used_cf': False,
            'used_cb': False,
            'interaction_count': 0,
            'avis_count': 0,
            'cold_start': True,
            'recommendation_status': 'error'
        }


def comparer_recommandations(user_id, nb=6):
    """
    Compare all three recommendation approaches for a user.
    
    Useful for A/B testing, debugging, and understanding algorithm behavior.
    Returns recommendations from all three strategies side-by-side.
    
    Args:
        user_id: Django User ID
        nb: Number of recommendations per strategy
        
    Returns:
        dict: Comparative results
        {
            'cf': [resto_id, ...],
            'cb': [resto_id, ...],
            'hybrid_weighted': [resto_id, ...],
            'hybrid_switching': [resto_id, ...],
            'hybrid_augmented': [resto_id, ...],
            'coverage': {...}
        }
    """
    try:
        start = time.time()
        
        from recommandation.engine import recommander_pour_utilisateur
        from recommandation.content_engine import recommander_content_based
        
        coverage = analyser_couverture_algorithme(user_id)
        
        results = {
            'cf': recommander_pour_utilisateur(user_id, nb),
            'cb': [r_id for r_id, _ in recommander_content_based(user_id, nb)],
            'hybrid_weighted': recommander_hybride(user_id, nb, alpha=0.6, strategy='weighted'),
            'hybrid_switching': recommander_hybride(user_id, nb, strategy='switching'),
            'hybrid_augmented': recommander_hybride(user_id, nb, alpha=0.6, strategy='feature_augmented'),
            'coverage': coverage
        }
        
        elapsed = time.time() - start
        logger.info(f'[HybridEngine:Comparer] user {user_id} comparison en {elapsed:.3f}s')
        
        return results
        
    except Exception as e:
        logger.error(f'[HybridEngine:Comparer] Erreur user {user_id}: {str(e)}')
        return {
            'cf': [],
            'cb': [],
            'hybrid_weighted': [],
            'hybrid_switching': [],
            'hybrid_augmented': [],
            'coverage': {}
        }
