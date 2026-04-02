from django.contrib import admin
from .models import Profil


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'ville', 'date_creation']
    search_fields = ['utilisateur__username', 'utilisateur__email']
