from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    icone = models.CharField(max_length=10, default='🍽️')
    slug = models.SlugField(unique=True, blank=True)
    cover_url = models.URLField(blank=True, help_text="URL image de la catégorie")

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Restaurant(models.Model):
    GAMME_CHOICES = [
        ('$', 'Économique (< 1000 FDJ)'),
        ('$$', 'Modéré (1000-3000 FDJ)'),
        ('$$$', 'Haut de gamme (> 3000 FDJ)'),
    ]

    nom = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    adresse = models.CharField(max_length=300)
    telephone = models.CharField(max_length=20, blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='restaurants')
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    cover_url = models.URLField(blank=True, help_text="URL image externe (Unsplash, etc.)")
    horaires = models.CharField(max_length=200, blank=True, help_text="Ex: Lun-Sam 7h-22h")
    site_web = models.URLField(blank=True)
    gamme_prix = models.CharField(max_length=3, choices=GAMME_CHOICES, default='$$')
    est_ouvert = models.BooleanField(default=True)
    est_vedette = models.BooleanField(default=False, verbose_name='Mis en avant')
    ajoute_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='restaurants_ajoutes')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ['-date_creation']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nom)
            slug = base_slug
            n = 1
            while Restaurant.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_image(self):
        if self.image:
            return self.image.url
        if self.cover_url:
            return self.cover_url
        return None

    def note_moyenne(self):
        from django.db.models import Avg
        result = self.avis.aggregate(Avg('note'))
        avg = result['note__avg']
        return round(avg, 1) if avg else 0

    def nombre_avis(self):
        return self.avis.count()

    def etoiles_plein(self):
        return range(int(self.note_moyenne()))

    def etoiles_vide(self):
        return range(5 - int(self.note_moyenne()))

    def __str__(self):
        return self.nom


class MenuItem(models.Model):
    TYPE_CHOICES = [
        ('plat', 'Plat'),
        ('boisson', 'Boisson'),
        ('cafe', 'Café & Dessert'),
    ]
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=8, decimal_places=0)
    type_item = models.CharField(max_length=20, choices=TYPE_CHOICES, default='plat')
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    cover_url = models.URLField(blank=True, help_text="URL image externe du plat")
    disponible = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item du menu'
        verbose_name_plural = 'Items du menu'
        ordering = ['type_item', 'nom']

    def get_image(self):
        if self.image:
            return self.image.url
        if self.cover_url:
            return self.cover_url
        return None

    def __str__(self):
        return f"{self.nom} - {self.restaurant.nom}"


class Avis(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avis')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='avis')
    note = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        unique_together = ('utilisateur', 'restaurant')
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.utilisateur.username} - {self.restaurant.nom} ({self.note}/5)"


class Favori(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoris')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='favoris')
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoris'
        unique_together = ('utilisateur', 'restaurant')
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.utilisateur.username} ♥ {self.restaurant.nom}"
