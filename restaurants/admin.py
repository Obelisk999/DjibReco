from django.contrib import admin
from .models import Categorie, Restaurant, MenuItem, Avis


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['icone', 'nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 2
    fields = ['nom', 'type_item', 'prix', 'disponible']


class AvisInline(admin.TabularInline):
    model = Avis
    extra = 0
    readonly_fields = ['utilisateur', 'note', 'commentaire', 'date_creation']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'adresse', 'est_ouvert', 'est_vedette', 'note_moyenne', 'date_creation']
    list_filter = ['categorie', 'est_ouvert', 'est_vedette']
    search_fields = ['nom', 'adresse']
    prepopulated_fields = {'slug': ('nom',)}
    inlines = [MenuItemInline, AvisInline]
    list_editable = ['est_ouvert', 'est_vedette']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['nom', 'restaurant', 'type_item', 'prix', 'disponible']
    list_filter = ['type_item', 'disponible', 'restaurant']
    search_fields = ['nom', 'restaurant__nom']
    list_editable = ['prix', 'disponible']


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'restaurant', 'note', 'date_creation']
    list_filter = ['note']
    search_fields = ['utilisateur__username', 'restaurant__nom']
    readonly_fields = ['date_creation']
