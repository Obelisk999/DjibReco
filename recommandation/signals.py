"""
recommandation/signals.py
Invalide le cache de recommandation dès qu'un utilisateur
laisse un avis ou modifie ses favoris, ou qu'un restaurant change.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from restaurants.models import Avis, Favori, Restaurant


def _invalider_cache(user_id: int):
    from .models import CacheRecommandation
    CacheRecommandation.objects.filter(utilisateur_id=user_id).delete()


def _invalider_cache_global():
    """Invalide le cache de TOUS les utilisateurs"""
    from .models import CacheRecommandation
    CacheRecommandation.objects.all().delete()


@receiver(post_save, sender=Avis)
def invalider_sur_nouvel_avis(sender, instance, **kwargs):
    _invalider_cache(instance.utilisateur_id)


@receiver(post_delete, sender=Avis)
def invalider_sur_suppression_avis(sender, instance, **kwargs):
    _invalider_cache(instance.utilisateur_id)


@receiver(post_save, sender=Favori)
def invalider_sur_nouveau_favori(sender, instance, **kwargs):
    _invalider_cache(instance.utilisateur_id)


@receiver(post_delete, sender=Favori)
def invalider_sur_suppression_favori(sender, instance, **kwargs):
    _invalider_cache(instance.utilisateur_id)


@receiver(post_save, sender=Restaurant)
def invalider_sur_modification_restaurant(sender, instance, created, **kwargs):
    """Invalider le cache de TOUS les utilisateurs quand un restaurant change"""
    if not created:  # Seulement si c'est une modification, pas une creation
        _invalider_cache_global()
