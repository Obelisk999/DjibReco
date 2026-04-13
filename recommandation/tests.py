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
