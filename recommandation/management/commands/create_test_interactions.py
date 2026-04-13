"""
recommandation/management/commands/create_test_interactions.py

Crée des utilisateurs, avis et interactions pour tester le système de recommandation.

Usage:
    python manage.py create_test_interactions
    python manage.py create_test_interactions --users 20 --interactions 100
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
import random
from restaurants.models import Restaurant, Avis, Favori
from recommandation.models import InteractionUtilisateur


class Command(BaseCommand):
    help = 'Crée des utilisateurs de test avec avis et interactions pour les recommandations'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Nombre d\'utilisateurs à créer (défaut: 10)'
        )
        parser.add_argument(
            '--interactions',
            type=int,
            default=50,
            help='Nombre total d\'interactions à créer (défaut: 50)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=30,
            help='Nombre total d\'avis à créer (défaut: 30)'
        )
    
    def handle(self, *args, **options):
        nb_users = options['users']
        nb_interactions = options['interactions']
        nb_reviews = options['reviews']
        
        # Récupérer les restaurants disponibles
        restaurants = list(Restaurant.objects.all())
        
        if not restaurants:
            self.stdout.write(
                self.style.ERROR('❌ Aucun restaurant trouvé. Exécutez d\'abord: '
                                'python manage.py seed_data')
            )
            return
        
        self.stdout.write(f'\n📊 Création de {nb_users} utilisateurs de test...')
        
        # 1. Créer les utilisateurs
        users = []
        for i in range(1, nb_users + 1):
            username = f'testuser{i}'
            email = f'test{i}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'Test User {i}',
                    'is_active': True,
                }
            )
            users.append(user)
            
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  ✓ {username}')
            else:
                self.stdout.write(f'  ◯ {username} (déjà existe)')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {len(users)} utilisateurs prêts')
        )
        
        # 2. Créer les avis (reviews)
        self.stdout.write(f'\n⭐ Création de {nb_reviews} avis...')
        
        avis_created = 0
        for _ in range(nb_reviews):
            user = random.choice(users)
            restaurant = random.choice(restaurants)
            note = random.randint(1, 5)
            
            # Un utilisateur ne peut noter qu'une fois par restaurant
            avis_obj, created = Avis.objects.get_or_create(
                utilisateur=user,
                restaurant=restaurant,
                defaults={
                    'note': note,
                    'commentaire': self._generate_comment(note),
                }
            )
            
            if created:
                avis_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {avis_created} avis créés')
        )
        
        # 3. Créer les favoris
        self.stdout.write(f'\n❤️  Création de favoris aléatoires...')
        
        favoris_created = 0
        for user in users:
            # Chaque utilisateur ajoute 2-4 favoris
            nb_favs = random.randint(2, 4)
            selected = random.sample(restaurants, min(nb_favs, len(restaurants)))
            
            for resto in selected:
                fav, created = Favori.objects.get_or_create(
                    utilisateur=user,
                    restaurant=resto
                )
                if created:
                    favoris_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {favoris_created} favoris créés')
        )
        
        # 4. Créer les interactions implicites
        self.stdout.write(f'\n👀 Création de {nb_interactions} interactions implicites...')
        
        interaction_types = ['vue', 'clic_menu', 'partage']
        inter_created = 0
        
        for _ in range(nb_interactions):
            user = random.choice(users)
            restaurant = random.choice(restaurants)
            type_action = random.choice(interaction_types)
            
            inter, created = InteractionUtilisateur.objects.get_or_create(
                utilisateur=user,
                restaurant=restaurant,
                type_action=type_action,
                defaults={'score': random.uniform(0.5, 2.0)}
            )
            
            if created:
                inter_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {inter_created} interactions créées')
        )
        
        # 5. Afficher les statistiques
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✨ DONNÉES DE TEST CRÉÉES AVEC SUCCÈS'))
        self.stdout.write(self.style.SUCCESS('='*60))
        
        total_avis = Avis.objects.count()
        total_inter = InteractionUtilisateur.objects.count()
        total_users = User.objects.count()
        total_favoris = Favori.objects.count()
        
        self.stdout.write(f'\n📈 Statistiques:')
        self.stdout.write(f'   👥 Utilisateurs totaux:        {total_users}')
        self.stdout.write(f'   ⭐ Avis totaux:                {total_avis}')
        self.stdout.write(f'   ❤️  Favoris totaux:             {total_favoris}')
        self.stdout.write(f'   👀 Interactions implicites:    {total_inter}')
        
        # Afficher quelques statistiques par utilisateur
        self.stdout.write(f'\n📊 Statistiques par utilisateur (avis, favoris, interactions):')
        for user in users[:3]:  # Afficher les 3 premiers
            avis_count = Avis.objects.filter(utilisateur=user).count()
            fav_count = Favori.objects.filter(utilisateur=user).count()
            inter_count = InteractionUtilisateur.objects.filter(utilisateur=user).count()
            self.stdout.write(
                f'   {user.username:20} → {avis_count:2} avis, '
                f'{fav_count:2} favoris, {inter_count:3} interactions'
            )
        
        if len(users) > 3:
            self.stdout.write(f'   ... et {len(users)-3} autres utilisateurs')
        
        self.stdout.write(f'\n🚀 Tester l\'API:')
        self.stdout.write(f'   GET /recommandations/pour-moi/')
        self.stdout.write(f'   (Connecté comme testuser1 / password123)')
        
        self.stdout.write(f'\n💾 Données conservées:')
        self.stdout.write(f'   - Les utilisateurs ne sont pas supprimés')
        self.stdout.write(f'   - Relancer la commande ajoute plus d\'interactions')
        self.stdout.write(f'   - Pour nettoyer: python manage.py flush recommandation')
    
    def _generate_comment(self, note):
        """Génère un commentaire aléatoire basé sur la note."""
        comments_by_rating = {
            1: [
                'Très décevant, ne recommande pas.',
                'Service inexistant et nourriture froide.',
                'Pire expérience de ma vie.',
                'À éviter absolument.',
                'Peu recommandable.',
            ],
            2: [
                'Pas terrible, manque de saveur.',
                'Correct mais sans plus.',
                'Peut mieux faire.',
                'Moyen, déçu.',
                'Acceptable mais cher pour la qualité.',
            ],
            3: [
                'Acceptable, rien d\'exceptionnnel.',
                'Bon rapport qualité-prix.',
                'Convenable pour un occasion rapide.',
                'Pas mal, à essayer.',
                'Honnête, correct.',
            ],
            4: [
                'Très bon ! Recommande.',
                'Excellente ambiance et bonne nourriture.',
                'Agréable surprenant.',
                'Haut qualité, service impeccable.',
                'Vraiment satisfait.',
            ],
            5: [
                'Exceptionnel ! Meilleur restaurant en ville.',
                'Un bijou culinaire, parfait en tous points.',
                'Restera dans mes meilleurs souvenirs.',
                'Service prestigieux, cuisine divine.',
                'À visiter absolument !',
            ]
        }
        
        return random.choice(comments_by_rating.get(note, ['Aucun commentaire']))
