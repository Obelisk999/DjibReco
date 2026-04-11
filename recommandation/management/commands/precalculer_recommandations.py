"""
recommandation/management/commands/precalculer_recommandations.py

Usage :
    python manage.py precalculer_recommandations
    python manage.py precalculer_recommandations --force   # ignore le cache existant
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from recommandation.engine import recommander_pour_utilisateur
from recommandation.models import CacheRecommandation


class Command(BaseCommand):
    help = 'Précalcule et met en cache les recommandations pour tous les utilisateurs actifs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Recalcule même si un cache récent existe',
        )
        parser.add_argument(
            '--nb',
            type=int,
            default=6,
            help='Nombre de recommandations à calculer par utilisateur (défaut: 6)',
        )

    def handle(self, *args, **options):
        force = options['force']
        nb    = options['nb']

        utilisateurs = User.objects.filter(is_active=True)
        total = utilisateurs.count()
        self.stdout.write(f'=== Précalcul des recommandations pour {total} utilisateurs ===')

        succes = erreurs = ignores = 0

        for user in utilisateurs:
            # Ignorer si cache frais et pas --force
            if not force:
                from datetime import timedelta
                from django.utils import timezone
                try:
                    cache = CacheRecommandation.objects.get(utilisateur=user)
                    age   = timezone.now() - cache.calculee_le
                    if age < timedelta(hours=1) and cache.restaurant_ids:
                        ignores += 1
                        continue
                except CacheRecommandation.DoesNotExist:
                    pass

            try:
                ids = recommander_pour_utilisateur(user.id, nb=nb)
                CacheRecommandation.objects.update_or_create(
                    utilisateur=user,
                    defaults={'restaurant_ids': ids}
                )
                self.stdout.write(f'  [OK] {user.username} → {len(ids)} recommandations')
                succes += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  [ERR] {user.username}: {e}')
                )
                erreurs += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nTerminé : {succes} calculés, {ignores} ignorés (cache frais), {erreurs} erreurs'
        ))
