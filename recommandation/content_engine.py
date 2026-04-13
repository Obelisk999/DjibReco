"""
Content-Based Filtering Engine for Restaurant Recommendations

Uses restaurant features (category, price, locality, tags) to recommend restaurants
similar to those the user has rated highly.

Feature Weighting:
  - Category: 40% (most important)
  - Price Range: 25%
  - Locality: 20%
  - Tags: 15%
  
TF-IDF Style Similarity: Calculates feature overlap between user preferences
and restaurant features, with fuzzy matching for text fields.
"""

import logging
import time
from math import sqrt
from collections import defaultdict
from django.db.models import Avg, Count, Q

logger = logging.getLogger(__name__)


def extraire_features_restaurant(restaurant):
    """
    Extract features from a restaurant for content-based matching.
    
    Args:
        restaurant: Restaurant model instance
        
    Returns:
        dict: Feature vector with normalized values
        {
            'category': string,
            'price_range': int (1-5),
            'locality': string,
            'tags': set of strings,
            'rating': float (0-5),
            'review_count': int
        }
    """
    try:
        start = time.time()
        
        # Get restaurant properties
        # Map gamme_prix to numeric scale
        price_map = {'$': 1, '$$': 2, '$$$': 3}
        price_range = price_map.get(restaurant.gamme_prix, 2) if hasattr(restaurant, 'gamme_prix') else 2
        
        # Get category name from ForeignKey
        category_name = restaurant.categorie.nom.lower() if restaurant.categorie else ''
        
        features = {
            'id': restaurant.id,
            'category': category_name,
            'price_range': price_range,
            'locality': restaurant.adresse.lower().strip() if hasattr(restaurant, 'adresse') else '',
            'name': restaurant.nom.lower() if hasattr(restaurant, 'nom') else '',
        }
        
        # Extract tags from description if available
        tags = set()
        if hasattr(restaurant, 'description') and restaurant.description:
            description = restaurant.description.lower()
            # Common restaurant attributes
            keywords = [
                'végétarien', 'vegan', 'halal', 'casher',
                'terrasse', 'climatisé', 'wifi', 'parking',
                'famille', 'couple', 'groupe', 'rapide',
                'authentique', 'moderne', 'traditionnel', 'fusion'
            ]
            for keyword in keywords:
                if keyword in description:
                    tags.add(keyword)
        
        features['tags'] = tags
        
        # Get rating statistics
        from restaurants.models import Avis
        avis = Avis.objects.filter(restaurant=restaurant)
        stats = avis.aggregate(
            avg_note=Avg('note'),
            count=Count('id')
        )
        
        features['rating'] = stats['avg_note'] or 3.0
        features['review_count'] = stats['count'] or 0
        
        elapsed = time.time() - start
        logger.debug(f'[ContentEngine:ExtractFeatures] resto {restaurant.id} en {elapsed:.3f}s')
        
        return features
        
    except Exception as e:
        logger.error(f'[ContentEngine:ExtractFeatures] Erreur resto {restaurant.id}: {str(e)}')
        return None


def construire_profil_utilisateur(user_id):
    """
    Build user preference vector from their highly-rated restaurants.
    
    Uses restaurants rated 4+ stars to determine user preferences.
    
    Args:
        user_id: User ID
        
    Returns:
        dict: User preference vector aggregating features from liked restaurants
        {
            'preferred_categories': {category: weight, ...},
            'preferred_price': float (1-5),
            'preferred_localities': {locality: weight, ...},
            'preferred_tags': {tag: weight, ...},
            'avg_rating_given': float,
            'rated_count': int
        }
    """
    try:
        start = time.time()
        
        from restaurants.models import Avis, Restaurant
        
        # Get restaurants rated 4+ by this user
        liked_restaurants = Restaurant.objects.filter(
            avis__utilisateur_id=user_id,
            avis__note__gte=4
        ).distinct()
        
        if not liked_restaurants.exists():
            # Cold-start: return neutral profile
            logger.debug(f'[ContentEngine:ProfilUtilisateur] user {user_id} pas de préférence')
            return {
                'preferred_categories': {},
                'preferred_price': 3.0,
                'preferred_localities': {},
                'preferred_tags': {},
                'avg_rating_given': 3.0,
                'rated_count': 0,
                'is_cold_start': True
            }
        
        # Collect features from liked restaurants
        profile = {
            'preferred_categories': defaultdict(float),
            'preferred_price': [],
            'preferred_localities': defaultdict(float),
            'preferred_tags': defaultdict(float),
            'avg_rating_given': 0.0,
            'rated_count': 0,
            'is_cold_start': False
        }
        
        total_rating = 0
        for restaurant in liked_restaurants:
            features = extraire_features_restaurant(restaurant)
            if not features:
                continue
            
            # Aggregate category preference
            if features['category']:
                profile['preferred_categories'][features['category']] += 1.0
            
            # Track price preferences
            profile['preferred_price'].append(features['price_range'])
            
            # Aggregate locality preference
            if features['locality']:
                profile['preferred_localities'][features['locality']] += 1.0
            
            # Aggregate tags
            for tag in features.get('tags', set()):
                profile['preferred_tags'][tag] += 1.0
            
            # Get actual rating given
            rating = Avis.objects.filter(
                utilisateur_id=user_id,
                restaurant=restaurant
            ).aggregate(avg=Avg('note'))['avg'] or 3.0
            total_rating += rating
            profile['rated_count'] += 1
        
        # Normalize counts to weights
        max_cat = max(profile['preferred_categories'].values()) if profile['preferred_categories'] else 1
        max_loc = max(profile['preferred_localities'].values()) if profile['preferred_localities'] else 1
        max_tag = max(profile['preferred_tags'].values()) if profile['preferred_tags'] else 1
        
        profile['preferred_categories'] = {
            k: v / max_cat for k, v in profile['preferred_categories'].items()
        }
        profile['preferred_localities'] = {
            k: v / max_loc for k, v in profile['preferred_localities'].items()
        }
        profile['preferred_tags'] = {
            k: v / max_tag for k, v in profile['preferred_tags'].items()
        }
        
        # Average price and rating
        profile['preferred_price'] = (
            sum(profile['preferred_price']) / len(profile['preferred_price'])
            if profile['preferred_price'] else 3.0
        )
        profile['avg_rating_given'] = (
            total_rating / profile['rated_count']
            if profile['rated_count'] > 0 else 3.0
        )
        
        elapsed = time.time() - start
        logger.info(f'[ContentEngine:ProfilUtilisateur] user {user_id} {profile["rated_count"]} restaurants (temps: {elapsed:.3f}s)')
        
        return profile
        
    except Exception as e:
        logger.error(f'[ContentEngine:ProfilUtilisateur] Erreur user {user_id}: {str(e)}')
        return {
            'preferred_categories': {},
            'preferred_price': 3.0,
            'preferred_localities': {},
            'preferred_tags': {},
            'avg_rating_given': 3.0,
            'rated_count': 0,
            'is_cold_start': True
        }


def similarite_contenu(user_profil, resto_features):
    """
    Calculate content-based similarity between user preferences and restaurant.
    
    Uses weighted feature matching with normalized scores.
    
    Args:
        user_profil: User preference vector from construire_profil_utilisateur()
        resto_features: Restaurant features from extraire_features_restaurant()
        
    Returns:
        float: Similarity score (0.0 - 1.0)
    """
    if not user_profil or not resto_features:
        return 0.0
    
    scores = []
    weights = {
        'category': 0.40,
        'price': 0.25,
        'locality': 0.20,
        'tags': 0.15
    }
    
    try:
        # Category similarity (0.40 weight)
        category_score = 0.0
        if resto_features['category'] and 'preferred_categories' in user_profil:
            preferred = user_profil['preferred_categories']
            if resto_features['category'] in preferred:
                category_score = min(1.0, preferred[resto_features['category']] * 1.2)
        scores.append(('category', category_score, weights['category']))
        
        # Price similarity (0.25 weight) - penalize deviations
        price_score = 0.0
        if user_profil['preferred_price'] > 0:
            price_diff = abs(resto_features['price_range'] - user_profil['preferred_price']) / 5.0
            price_score = max(0.0, 1.0 - price_diff)
        scores.append(('price', price_score, weights['price']))
        
        # Locality similarity (0.20 weight)
        locality_score = 0.0
        if resto_features['locality'] and 'preferred_localities' in user_profil:
            preferred = user_profil['preferred_localities']
            if resto_features['locality'] in preferred:
                locality_score = min(1.0, preferred[resto_features['locality']] * 1.2)
        scores.append(('locality', locality_score, weights['locality']))
        
        # Tags similarity (0.15 weight)
        tag_score = 0.0
        if resto_features['tags'] and 'preferred_tags' in user_profil:
            preferred = user_profil['preferred_tags']
            matches = sum(
                preferred.get(tag, 0) for tag in resto_features['tags']
                if tag in preferred
            )
            if preferred:  # Avoid division by zero
                tag_score = matches / len(preferred) if preferred else 0
                tag_score = min(1.0, tag_score * 1.5)
        scores.append(('tags', tag_score, weights['tags']))
        
        # Weighted sum
        total_score = sum(score * weight for _, score, weight in scores)
        
        # Boost if restaurant rating is good
        rating_boost = min(0.2, (resto_features['rating'] - 2.5) / 10.0)
        total_score = min(1.0, total_score + rating_boost)
        
        return max(0.0, total_score)
        
    except Exception as e:
        logger.error(f'[ContentEngine:Similarite] Erreur calcul: {str(e)}')
        return 0.0


def recommander_content_based(user_id, nb=6):
    """
    Generate content-based recommendations for a user.
    
    Recommends restaurants similar to those the user has rated highly,
    excluding restaurants they've already rated.
    
    Args:
        user_id: Django User ID
        nb: Number of recommendations to return (default 6)
        
    Returns:
        list: Restaurant IDs sorted by content similarity score
              [(resto_id, similarity_score), ...]
    """
    try:
        start = time.time()
        
        from restaurants.models import Restaurant, Avis
        
        # Get user profile
        user_profil = construire_profil_utilisateur(user_id)
        
        # Get all restaurants not yet rated by user
        rated_restaurants = Avis.objects.filter(
            utilisateur_id=user_id
        ).values_list('restaurant_id', flat=True)
        
        candidates = Restaurant.objects.exclude(id__in=rated_restaurants)
        
        # Score each restaurant
        recommendations = []
        for restaurant in candidates[:500]:  # Limit computation
            features = extraire_features_restaurant(restaurant)
            if not features:
                continue
            
            similarity = similarite_contenu(user_profil, features)
            
            # Add modulation based on restaurant rating and review count
            if features['review_count'] > 0:
                confidence = min(1.0, features['review_count'] / 20.0)
            else:
                confidence = 0.3
            
            final_score = similarity * (0.7 + 0.3 * confidence)
            recommendations.append((restaurant.id, final_score))
        
        # Sort by score and limit
        recommendations.sort(key=lambda x: x[1], reverse=True)
        result = recommendations[:nb]
        
        elapsed = time.time() - start
        logger.info(f'[ContentEngine:Recommander] user {user_id} → {len(result)} recommendations (temps: {elapsed:.3f}s)')
        
        return result
        
    except Exception as e:
        logger.error(f'[ContentEngine:Recommander] Erreur user {user_id}: {str(e)}')
        return []
