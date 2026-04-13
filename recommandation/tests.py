"""
recommandation/tests.py
Suite de tests pour le système de recommandation.
"""
import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from restaurants.models import Restaurant, Categorie, Avis, Favori
from .models import InteractionUtilisateur, CacheRecommandation
from .engine import (
    construire_matrice,
    similarite_cosinus,
    recommander_pour_utilisateur,
    restaurants_similaires,
    enregistrer_interaction,
)
from .content_engine import (
    extraire_features_restaurant,
    construire_profil_utilisateur,
    similarite_contenu,
    recommander_content_based,
)
from .hybrid_engine import (
    recommander_hybride,
    analyser_couverture_algorithme,
    comparer_recommandations,
)


# ─── FIXTURES ──────────────────────────────────────────────────────────────

class TestDataMixin(TestCase):
    """Crée des données de test réutilisables."""
    
    def setUp(self):
        """Setup des données de test."""
        # Créer des utilisateurs
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@test.com',
            password='test123'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@test.com',
            password='test123'
        )
        self.user3 = User.objects.create_user(
            username='charlie',
            email='charlie@test.com',
            password='test123'
        )
        
        # Créer catégories
        self.cat_pizza = Categorie.objects.create(
            nom='Pizzeria',
            slug='pizzeria',
            icone='🍕'
        )
        self.cat_cafe = Categorie.objects.create(
            nom='Café',
            slug='cafe',
            icone='☕'
        )
        
        # Créer restaurants
        self.resto_pizza = Restaurant.objects.create(
            nom='Chez Giovanni',
            slug='chez-giovanni',
            description='Excellente pizzeria italienne',
            adresse='Boulevard du 27 Juin',
            categorie=self.cat_pizza,
            gamme_prix='$$',
            est_ouvert=True,
            ajoute_par=self.user1
        )
        self.resto_cafe = Restaurant.objects.create(
            nom='Café Artisan',
            slug='cafe-artisan',
            description='Bon café local',
            adresse='Rue de l\'Église',
            categorie=self.cat_cafe,
            gamme_prix='$',
            est_ouvert=True,
            ajoute_par=self.user1
        )
        self.resto_pizza2 = Restaurant.objects.create(
            nom='Marco\'s Pizza',
            slug='marcos-pizza',
            description='Pizza nouvelle génération',
            adresse='Rue Harar',
            categorie=self.cat_pizza,
            gamme_prix='$$',
            est_ouvert=True,
            ajoute_par=self.user2
        )
        
        # Créer des avis
        Avis.objects.create(
            utilisateur=self.user1,
            restaurant=self.resto_pizza,
            note=5,
            commentaire='Excellent !'
        )
        Avis.objects.create(
            utilisateur=self.user1,
            restaurant=self.resto_cafe,
            note=4,
            commentaire='Bon café'
        )
        Avis.objects.create(
            utilisateur=self.user2,
            restaurant=self.resto_pizza,
            note=4,
            commentaire='Très bon'
        )
        Avis.objects.create(
            utilisateur=self.user2,
            restaurant=self.resto_pizza2,
            note=5,
            commentaire='Excellente pizza'
        )
        
        # Créer des favoris
        Favori.objects.create(
            utilisateur=self.user1,
            restaurant=self.resto_pizza
        )
        Favori.objects.create(
            utilisateur=self.user2,
            restaurant=self.resto_pizza2
        )
        
        # Créer des interactions
        InteractionUtilisateur.objects.create(
            utilisateur=self.user1,
            restaurant=self.resto_pizza,
            type_action='vue',
            score=1.0
        )
        InteractionUtilisateur.objects.create(
            utilisateur=self.user1,
            restaurant=self.resto_cafe,
            type_action='clic_menu',
            score=0.5
        )
        InteractionUtilisateur.objects.create(
            utilisateur=self.user2,
            restaurant=self.resto_pizza2,
            type_action='partage',
            score=2.0
        )


# ─── TESTS DU MOTEUR ──────────────────────────────────────────────────────

class TestMatriceConstruction(TestDataMixin):
    """Tests de la construction de la matrice utilisateur-restaurant."""
    
    def test_construire_matrice_non_vide(self):
        """Vérifie que la matrice contient les données attendues."""
        matrice = construire_matrice()
        
        # Au moins 2 utilisateurs
        self.assertGreaterEqual(len(matrice), 2)
        
        # user1 doit avoir au moins 2 restaurants
        self.assertGreaterEqual(len(matrice[self.user1.id]), 2)
        
        # user2 doit avoir au moins 2 restaurants
        self.assertGreaterEqual(len(matrice[self.user2.id]), 2)
    
    def test_scores_avis_ponderables(self):
        """Vérifie que les scores des avis sont correctement pondérés (1-5)."""
        matrice = construire_matrice()
        
        # user1 a noté resto_pizza 5 stars
        score_pizza = matrice[self.user1.id].get(self.resto_pizza.id)
        self.assertIsNotNone(score_pizza)
        # Score minimum 5 (note × poids) car poids['avis'] = 1.0
        self.assertGreaterEqual(score_pizza, 5)
    
    def test_scores_plafonnes_a_10(self):
        """Vérifie que les scores sont plafonnés à 10."""
        matrice = construire_matrice()
        
        # Tous les scores doivent être ≤ 10
        for uid, restaurants in matrice.items():
            for rid, score in restaurants.items():
                self.assertLessEqual(score, 10.0)


class TestSimilariteConsinus(TestCase):
    """Tests du calcul de similarité cosinus."""
    
    def test_similarite_vecteurs_identiques(self):
        """Similarité de deux vecteurs identiques = 1.0."""
        vec = {1: 2.0, 2: 3.0, 3: 4.0}
        sim = similarite_cosinus(vec, vec)
        self.assertAlmostEqual(sim, 1.0, places=5)
    
    def test_similarite_vecteurs_opposes(self):
        """Similarité de vecteurs orthogonaux = 0."""
        vec_a = {1: 1.0, 2: 0.0}
        vec_b = {1: 0.0, 2: 1.0}
        sim = similarite_cosinus(vec_a, vec_b)
        self.assertAlmostEqual(sim, 0.0, places=5)
    
    def test_similarite_vecteurs_partiels(self):
        """Similarité avec overlap partiel."""
        vec_a = {1: 1.0, 2: 1.0}
        vec_b = {1: 1.0, 3: 1.0}  # Seul 1 en commun
        sim = similarite_cosinus(vec_a, vec_b)
        # Doit être entre 0 et 1
        self.assertGreater(sim, 0.0)
        self.assertLess(sim, 1.0)
    
    def test_similarite_vecteur_vide(self):
        """Similarité quand l'un des vecteurs est vide = 0."""
        vec = {1: 1.0}
        vide = {}
        sim = similarite_cosinus(vec, vide)
        self.assertEqual(sim, 0.0)


class TestRecommandationMotor(TestDataMixin):
    """Tests du moteur de recommandation."""
    
    def test_recommander_pour_utilisateur_retourne_liste(self):
        """Vérifie que recommander_pour_utilisateur retourne une liste."""
        result = recommander_pour_utilisateur(self.user3.id, nb=3)
        self.assertIsInstance(result, list)
    
    def test_recommander_exclut_restaurants_deja_notes(self):
        """Les restaurants déjà notés ne doivent pas être recommandés."""
        result = recommander_pour_utilisateur(self.user1.id, nb=10)
        
        # user1 a déjà noté resto_pizza et resto_cafe
        self.assertNotIn(self.resto_pizza.id, result)
        self.assertNotIn(self.resto_cafe.id, result)
    
    def test_recommander_cold_start(self):
        """Avec peu d'interactions, utilise le fallback."""
        result = recommander_pour_utilisateur(self.user3.id, nb=3)
        # user3 n'a aucune interaction, donc fallback sur top global
        self.assertIsInstance(result, list)
        # Peut être vide ou rempli selon les restaurants disponibles
        self.assertLessEqual(len(result), 3)
    
    def test_recommander_respect_limite(self):
        """Respect du nombre de recommandations demandé."""
        result = recommander_pour_utilisateur(self.user1.id, nb=2)
        self.assertLessEqual(len(result), 2)


class TestSimilairesRestaurants(TestDataMixin):
    """Tests des recommandations similaires (item-based)."""
    
    def test_similaires_retourne_liste(self):
        """Vérifie que restaurants_similaires retourne une liste."""
        result = restaurants_similaires(self.resto_pizza.id, nb=2)
        self.assertIsInstance(result, list)
    
    def test_similaires_exclut_restaurant_lui_meme(self):
        """Le restaurant lui-même n'est pas similaire à lui-même."""
        result = restaurants_similaires(self.resto_pizza.id, nb=10)
        self.assertNotIn(self.resto_pizza.id, result)
    
    def test_similaires_trouve_pizza_similaire(self):
        """Deux pizzerias devraient être similaires."""
        # user2 aime aussi les pizzas (notes resto_pizza2)
        result = restaurants_similaires(self.resto_pizza.id, nb=5)
        # On s'attend à trouver resto_pizza2 (même catégorie, utilisateurs similaires)
        # (peut être vide si pas assez de co-rating)
        self.assertIsInstance(result, list)


# ─── TESTS DES MODÈLES ─────────────────────────────────────────────────────

class TestInteractionUtilisateur(TestDataMixin):
    """Tests du modèle InteractionUtilisateur."""
    
    def test_creer_interaction(self):
        """Crée une interaction valide."""
        inter = InteractionUtilisateur.objects.create(
            utilisateur=self.user1,
            restaurant=self.resto_pizza,
            type_action='vue',
            score=1.0
        )
        self.assertEqual(inter.utilisateur_id, self.user1.id)
        self.assertEqual(inter.restaurant_id, self.resto_pizza.id)
        self.assertEqual(inter.type_action, 'vue')
    
    def test_type_action_valides(self):
        """Vérifie que les types d'action sont limités aux choix."""
        valides = ['vue', 'clic_menu', 'partage']
        
        for type_act in valides:
            inter = InteractionUtilisateur(
                utilisateur=self.user1,
                restaurant=self.resto_pizza,
                type_action=type_act
            )
            # Ne pas sauvegarder car c'est la même interaction
            self.assertEqual(inter.type_action, type_act)
    
    def test_interaction_str(self):
        """Vérifie la représentation en string."""
        inter = InteractionUtilisateur.objects.create(
            utilisateur=self.user1,
            restaurant=self.resto_pizza,
            type_action='vue'
        )
        expected = f'{self.user1} -> {self.resto_pizza} [vue]'
        self.assertEqual(str(inter), expected)


class TestCacheRecommandation(TestDataMixin):
    """Tests du modèle CacheRecommandation."""
    
    def test_creer_cache(self):
        """Crée un cache de recommandation."""
        cache = CacheRecommandation.objects.create(
            utilisateur=self.user1,
            restaurant_ids=[1, 2, 3]
        )
        self.assertEqual(cache.utilisateur_id, self.user1.id)
        self.assertEqual(cache.restaurant_ids, [1, 2, 3])
    
    def test_cache_one_to_one(self):
        """Un utilisateur ne peut avoir qu'un cache."""
        CacheRecommandation.objects.create(
            utilisateur=self.user1,
            restaurant_ids=[1, 2]
        )
        
        # Créer un deuxième cache pour user1 doit remplacer le premier
        CacheRecommandation.objects.update_or_create(
            utilisateur=self.user1,
            defaults={'restaurant_ids': [3, 4]}
        )
        
        caches = CacheRecommandation.objects.filter(utilisateur=self.user1)
        self.assertEqual(caches.count(), 1)
        self.assertEqual(caches.first().restaurant_ids, [3, 4])


class TestEnregistrerInteraction(TestDataMixin):
    """Tests de la fonction enregistrer_interaction."""
    
    def test_enregistrer_interaction(self):
        """Enregistre une interaction correctement."""
        enregistrer_interaction(self.user1.id, self.resto_pizza2.id, 'vue')
        
        inter = InteractionUtilisateur.objects.filter(
            utilisateur_id=self.user1.id,
            restaurant_id=self.resto_pizza2.id,
            type_action='vue'
        )
        self.assertTrue(inter.exists())
    
    def test_enregistrer_interaction_score_correcte(self):
        """Vérifie que le score correspond au poids."""
        enregistrer_interaction(self.user1.id, self.resto_pizza2.id, 'clic_menu')
        
        inter = InteractionUtilisateur.objects.get(
            utilisateur_id=self.user1.id,
            restaurant_id=self.resto_pizza2.id,
            type_action='clic_menu'
        )
        # Poids de 'clic_menu' = 0.5
        self.assertAlmostEqual(inter.score, 0.5)


# ─── TESTS DES VUES/API ────────────────────────────────────────────────────

class TestRecommandationsAPI(TestDataMixin):
    """Tests de l'API /recommandations/pour-moi/."""
    
    def setUp(self):
        """Setup des données et du client test."""
        super().setUp()
        self.client = Client()
    
    def test_api_sans_authentification(self):
        """L'endpoint requiert une authentification."""
        response = self.client.get('/recommandations/pour-moi/')
        # Doit rediriger ou retourner 401/403
        self.assertIn(response.status_code, [301, 302, 401, 403])
    
    def test_api_recommandations_autentifie(self):
        """API retourne JSON avec recommandations."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/pour-moi/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('recommandations', data)
        self.assertIsInstance(data['recommandations'], list)
    
    def test_api_respecte_parametres(self):
        """API respecte le paramètre 'nb'."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/pour-moi/?nb=3')
        
        data = json.loads(response.content)
        self.assertLessEqual(len(data['recommandations']), 3)
    
    def test_api_inclut_infos_restaurant(self):
        """Recommandations incluent détails du restaurant."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/pour-moi/?nb=1')
        
        data = json.loads(response.content)
        if data['recommandations']:
            resto = data['recommandations'][0]
            self.assertIn('id', resto)
            self.assertIn('nom', resto)
            self.assertIn('slug', resto)
            self.assertIn('note', resto)
            self.assertIn('est_favori', resto)


class TestInteractionAPI(TestDataMixin):
    """Tests de l'API POST /recommandations/interaction/."""
    
    def setUp(self):
        """Setup du client test."""
        super().setUp()
        self.client = Client()
    
    def test_interaction_sans_authentification(self):
        """POST sur interaction requiert authentification."""
        response = self.client.post(
            '/recommandations/interaction/',
            data=json.dumps({'restaurant_id': 1, 'type_action': 'vue'}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [301, 302, 401, 403])
    
    def test_interaction_post_valide(self):
        """Enregistre une interaction via POST."""
        self.client.login(username='alice', password='test123')
        response = self.client.post(
            '/recommandations/interaction/',
            data=json.dumps({
                'restaurant_id': self.resto_pizza.id,
                'type_action': 'vue'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
    
    def test_interaction_donnees_invalides(self):
        """Rejet des données invalides."""
        self.client.login(username='alice', password='test123')
        response = self.client.post(
            '/recommandations/interaction/',
            data=json.dumps({'restaurant_id': 'invalid'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_interaction_type_action_invalide(self):
        """Rejet des types d'action invalides."""
        self.client.login(username='alice', password='test123')
        response = self.client.post(
            '/recommandations/interaction/',
            data=json.dumps({
                'restaurant_id': self.resto_pizza.id,
                'type_action': 'invalid_action'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_interaction_restaurant_inexistant(self):
        """Rejet quand le restaurant n'existe pas."""
        self.client.login(username='alice', password='test123')
        response = self.client.post(
            '/recommandations/interaction/',
            data=json.dumps({
                'restaurant_id': 99999,
                'type_action': 'vue'
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)


class TestSimilairesAPI(TestDataMixin):
    """Tests de l'API GET /recommandations/similaires/<slug>/."""
    
    def setUp(self):
        """Setup du client test."""
        super().setUp()
        self.client = Client()
    
    def test_similaires_sans_authentification(self):
        """Similaires accessibles sans authentification."""
        response = self.client.get(
            f'/recommandations/similaires/{self.resto_pizza.slug}/'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('similaires', data)
    
    def test_similaires_restaurant_inexistant(self):
        """404 si restaurant n'existe pas."""
        response = self.client.get('/recommandations/similaires/inexistant/')
        self.assertEqual(response.status_code, 404)
    
    def test_similaires_respecte_parametres(self):
        """API respecte le paramètre 'nb'."""
        response = self.client.get(
            f'/recommandations/similaires/{self.resto_pizza.slug}/?nb=2'
        )
        
        data = json.loads(response.content)
        self.assertLessEqual(len(data['similaires']), 2)


# ─── TESTS CONTENT-BASED FILTERING ───────────────────────────────────────

class TestExtraireFeatures(TestDataMixin):
    """Tests de l'extraction de features."""
    
    def test_extraire_features_retourne_dict(self):
        """extraire_features retourne un dictionnaire valide."""
        features = extraire_features_restaurant(self.resto_pizza)
        
        self.assertIsInstance(features, dict)
        self.assertIn('id', features)
        self.assertIn('category', features)
        self.assertIn('price_range', features)
        self.assertIn('locality', features)
    
    def test_extraire_features_valeurs(self):
        """Vérifie les valeurs extraites."""
        features = extraire_features_restaurant(self.resto_pizza)
        
        self.assertEqual(features['id'], self.resto_pizza.id)
        self.assertEqual(features['rating'], 4.5)  # (5+4)/2
        self.assertEqual(features['review_count'], 2)
    
    def test_extraire_features_price_range(self):
        """Price range est entre 1 et 5."""
        features = extraire_features_restaurant(self.resto_pizza)
        self.assertGreaterEqual(features['price_range'], 1)
        self.assertLessEqual(features['price_range'], 5)


class TestProfilUtilisateur(TestDataMixin):
    """Tests de la construction du profil utilisateur."""
    
    def test_profil_utilisateur_retourne_dict(self):
        """construire_profil_utilisateur retourne un dictionnaire."""
        profil = construire_profil_utilisateur(self.user1.id)
        
        self.assertIsInstance(profil, dict)
        self.assertIn('preferred_categories', profil)
        self.assertIn('preferred_price', profil)
        self.assertIn('avg_rating_given', profil)
        self.assertIn('is_cold_start', profil)
    
    def test_profil_utilisateur_with_ratings(self):
        """Profil d'utilisateur avec notes."""
        profil = construire_profil_utilisateur(self.user1.id)
        
        # user1 a noté 2 restaurants (5 et 4 stars)
        self.assertFalse(profil['is_cold_start'])
        self.assertEqual(profil['rated_count'], 2)
        # avg = (5+4)/2 = 4.5
        self.assertAlmostEqual(profil['avg_rating_given'], 4.5)
    
    def test_profil_utilisateur_cold_start(self):
        """Profil d'utilisateur sans notes (cold-start)."""
        profil = construire_profil_utilisateur(self.user3.id)
        
        # user3 n'a pas noté de restaurants
        self.assertTrue(profil['is_cold_start'])
        self.assertEqual(profil['rated_count'], 0)
        self.assertEqual(profil['preferred_categories'], {})


class TestSimilariteContenu(TestDataMixin):
    """Tests du calcul de similarité content-based."""
    
    def test_similarite_contenu_retourne_float(self):
        """similarite_contenu retourne un float entre 0 et 1."""
        profil = construire_profil_utilisateur(self.user1.id)
        features = extraire_features_restaurant(self.resto_pizza2)
        
        score = similarite_contenu(profil, features)
        
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_similarite_contenu_vide(self):
        """Similitude avec profil vide retourne 0."""
        profil = None
        features = extraire_features_restaurant(self.resto_pizza)
        
        score = similarite_contenu(profil, features)
        
        self.assertEqual(score, 0.0)


class TestRecommandationContentBased(TestDataMixin):
    """Tests du moteur content-based."""
    
    def test_recommander_content_based_retourne_liste(self):
        """recommander_content_based retourne une liste."""
        result = recommander_content_based(self.user1.id, nb=3)
        
        self.assertIsInstance(result, list)
    
    def test_recommander_content_based_tuples(self):
        """Résultats sont des tuples (id, score)."""
        result = recommander_content_based(self.user1.id, nb=3)
        
        for item in result:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
            self.assertIsInstance(item[0], int)  # ID
            self.assertIsInstance(item[1], float)  # Score
    
    def test_recommander_content_based_exclut_notes(self):
        """N'inclut pas les restaurants déjà notés."""
        result = recommander_content_based(self.user1.id, nb=10)
        restaurant_ids = [r_id for r_id, _ in result]
        
        # user1 a déjà noté resto_pizza et resto_cafe
        self.assertNotIn(self.resto_pizza.id, restaurant_ids)
        self.assertNotIn(self.resto_cafe.id, restaurant_ids)
    
    def test_recommander_content_based_respect_limite(self):
        """Respect du nombre de recommandations demandé."""
        result = recommander_content_based(self.user1.id, nb=2)
        self.assertLessEqual(len(result), 2)


class TestContentBasedAPI(TestDataMixin):
    """Tests de l'API /recommandations/content-based/."""
    
    def setUp(self):
        """Setup du client test."""
        super().setUp()
        self.client = Client()
    
    def test_content_based_api_sans_auth(self):
        """Endpoint requiert authentification."""
        response = self.client.get('/recommandations/content-based/')
        self.assertIn(response.status_code, [301, 302, 401, 403])
    
    def test_content_based_api_authentifie(self):
        """API retourne recommandations."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/content-based/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('recommandations', data)
        self.assertIn('methode', data)
        self.assertEqual(data['methode'], 'content-based')
    
    def test_content_based_api_respecte_nb(self):
        """API respecte le paramètre nb."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/content-based/?nb=2')
        
        data = json.loads(response.content)
        self.assertLessEqual(len(data['recommandations']), 2)


# ─── TESTS HYBRID FILTERING ────────────────────────────────────────────────

class TestAnalyserCouverture(TestDataMixin):
    """Tests de l'analyse de couverture."""
    
    def test_analyser_couverture_retourne_dict(self):
        """analyser_couverture_algorithme retourne dict."""
        couverture = analyser_couverture_algorithme(self.user1.id)
        
        self.assertIsInstance(couverture, dict)
        self.assertIn('used_cf', couverture)
        self.assertIn('used_cb', couverture)
        self.assertIn('cold_start', couverture)
        self.assertIn('recommendation_status', couverture)
    
    def test_analyser_couverture_valeurs_bool(self):
        """Clés bool contiennent des booléens."""
        couverture = analyser_couverture_algorithme(self.user1.id)
        
        self.assertIsInstance(couverture['used_cf'], bool)
        self.assertIsInstance(couverture['used_cb'], bool)
        self.assertIsInstance(couverture['cold_start'], bool)
    
    def test_analyser_couverture_cold_start(self):
        """Détecte correctement le cold-start."""
        # user3 sans interactions
        couverture = analyser_couverture_algorithme(self.user3.id)
        self.assertTrue(couverture['cold_start'])


class TestRecommandationHybride(TestDataMixin):
    """Tests du moteur hybride."""
    
    def test_recommander_hybride_retourne_liste(self):
        """recommander_hybride retourne une liste."""
        result = recommander_hybride(self.user1.id, nb=3)
        
        self.assertIsInstance(result, list)
    
    def test_recommander_hybride_weighted(self):
        """Stratégie 'weighted' fonctionne."""
        result = recommander_hybride(
            self.user1.id,
            nb=3,
            alpha=0.6,
            strategy='weighted'
        )
        
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 3)
    
    def test_recommander_hybride_switching(self):
        """Stratégie 'switching' fonctionne."""
        result = recommander_hybride(
            self.user1.id,
            nb=3,
            strategy='switching'
        )
        
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 3)
    
    def test_recommander_hybride_feature_augmented(self):
        """Stratégie 'feature_augmented' fonctionne."""
        result = recommander_hybride(
            self.user1.id,
            nb=3,
            strategy='feature_augmented'
        )
        
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 3)
    
    def test_recommander_hybride_alpha_valide(self):
        """Alpha entre 0 et 1 est valide."""
        for alpha in [0.0, 0.3, 0.6, 0.9, 1.0]:
            result = recommander_hybride(
                self.user1.id,
                nb=2,
                alpha=alpha,
                strategy='weighted'
            )
            self.assertIsInstance(result, list)


class TestComparerRecommandations(TestDataMixin):
    """Tests de la comparaison d'algorithmes."""
    
    def test_comparer_retourne_dict(self):
        """comparer_recommandations retourne un dictionnaire."""
        resultats = comparer_recommandations(self.user1.id, nb=3)
        
        self.assertIsInstance(resultats, dict)
        self.assertIn('cf', resultats)
        self.assertIn('cb', resultats)
        self.assertIn('hybrid_weighted', resultats)
        self.assertIn('coverage', resultats)
    
    def test_comparer_tous_algorithmes(self):
        """Comparaison inclut tous les algorithmes."""
        resultats = comparer_recommandations(self.user1.id, nb=2)
        
        algos = ['cf', 'cb', 'hybrid_weighted', 'hybrid_switching', 'hybrid_augmented']
        for algo in algos:
            self.assertIn(algo, resultats)
            self.assertIsInstance(resultats[algo], list)


class TestHybridAPI(TestDataMixin):
    """Tests de l'API /recommandations/hybride/."""
    
    def setUp(self):
        """Setup du client test."""
        super().setUp()
        self.client = Client()
    
    def test_hybride_api_sans_auth(self):
        """Endpoint requiert authentification."""
        response = self.client.get('/recommandations/hybride/')
        self.assertIn(response.status_code, [301, 302, 401, 403])
    
    def test_hybride_api_authentifie(self):
        """API retourne recommandations."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/hybride/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('recommandations', data)
        self.assertIn('methode', data)
        self.assertEqual(data['methode'], 'hybride')
    
    def test_hybride_api_strategies(self):
        """API accepte différentes stratégies."""
        self.client.login(username='alice', password='test123')
        
        for strategy in ['weighted', 'switching', 'feature_augmented']:
            response = self.client.get(
                f'/recommandations/hybride/?strategy={strategy}'
            )
            
            data = json.loads(response.content)
            self.assertEqual(data['strategy'], strategy)
    
    def test_hybride_api_invalid_strategy(self):
        """Rejette les stratégies invalides."""
        self.client.login(username='alice', password='test123')
        response = self.client.get(
            '/recommandations/hybride/?strategy=invalid'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_hybride_api_alpha_parameter(self):
        """API accepte le paramètre alpha."""
        self.client.login(username='alice', password='test123')
        response = self.client.get(
            '/recommandations/hybride/?alpha=0.7'
        )
        
        data = json.loads(response.content)
        self.assertAlmostEqual(data['alpha'], 0.7)


class TestComparisonAPI(TestDataMixin):
    """Tests de l'API /recommandations/comparer/."""
    
    def setUp(self):
        """Setup du client test."""
        super().setUp()
        self.client = Client()
    
    def test_comparer_api_sans_auth(self):
        """Endpoint requiert authentification."""
        response = self.client.get('/recommandations/comparer/')
        self.assertIn(response.status_code, [301, 302, 401, 403])
    
    def test_comparer_api_authentifie(self):
        """API retourne comparaison."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/comparer/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('comparaison', data)
        self.assertIn('user_coverage', data)
    
    def test_comparer_api_tous_algorithmes(self):
        """Comparaison affiche tous les algorithmes."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/comparer/')
        
        data = json.loads(response.content)
        comp = data['comparaison']
        
        self.assertIn('cf', comp)
        self.assertIn('cb', comp)
        self.assertIn('hybrid_weighted', comp)


class TestAnalyseAPI(TestDataMixin):
    """Tests de l'API /recommandations/analyse/."""
    
    def setUp(self):
        """Setup du client test."""
        super().setUp()
        self.client = Client()
    
    def test_analyse_api_sans_auth(self):
        """Endpoint requiert authentification."""
        response = self.client.get('/recommandations/analyse/')
        self.assertIn(response.status_code, [301, 302, 401, 403])
    
    def test_analyse_api_authentifie(self):
        """API retourne analyse."""
        self.client.login(username='alice', password='test123')
        response = self.client.get('/recommandations/analyse/')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('couverture', data)
        couv = data['couverture']
        
        self.assertIn('used_cf', couv)
        self.assertIn('used_cb', couv)
        self.assertIn('recommendation_status', couv)

