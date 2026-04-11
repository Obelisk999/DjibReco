"""
recommandation/signals.py
Invalide le cache de recommandation dès qu'un utilisateur
laisse un avis ou modifie ses favoris.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from restaurants.models import Avis, Favori


def _invalider_cache(user_id: int):
    from .models import CacheRecommandation
    CacheRecommandation.objects.filter(utilisateur_id=user_id).delete()


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
