"""
recommandation/models.py
"""
from django.db import models
from django.contrib.auth.models import User
from restaurants.models import Restaurant


class InteractionUtilisateur(models.Model):
    TYPE_CHOICES = [
        ('vue',        'Vue restaurant'),
        ('clic_menu',  'Clic sur item menu'),
        ('partage',    'Partage'),
    ]
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions_reco')
    restaurant  = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='interactions_reco')
    type_action = models.CharField(max_length=20, choices=TYPE_CHOICES)
    score       = models.FloatField(default=1.0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['utilisateur', 'restaurant']),
            models.Index(fields=['type_action']),
        ]
        verbose_name        = 'Interaction utilisateur'
        verbose_name_plural = 'Interactions utilisateurs'

    def __str__(self):
        return f'{self.utilisateur} -> {self.restaurant} [{self.type_action}]'


class CacheRecommandation(models.Model):
    """
    Cache des recommandations calculées (TTL : 1h par défaut).
    Invalidé lors d'un nouvel avis ou favori via signal.
    """
    utilisateur    = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cache_reco')
    restaurant_ids = models.JSONField(default=list)
    calculee_le    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Cache recommandation'
        verbose_name_plural = 'Caches recommandations'

    def __str__(self):
        return f'Cache reco pour {self.utilisateur} ({len(self.restaurant_ids)} items)'
