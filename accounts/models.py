from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profil(models.Model):
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    ville = models.CharField(max_length=100, default='Djibouti')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"


@receiver(post_save, sender=User)
def creer_profil(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(utilisateur=instance)


@receiver(post_save, sender=User)
def sauvegarder_profil(sender, instance, **kwargs):
    if hasattr(instance, 'profil'):
        instance.profil.save()
