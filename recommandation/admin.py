"""
recommandation/admin.py
"""
from django.contrib import admin
from .models import InteractionUtilisateur, CacheRecommandation


@admin.register(InteractionUtilisateur)
class InteractionAdmin(admin.ModelAdmin):
    list_display  = ['utilisateur', 'restaurant', 'type_action', 'score', 'created_at']
    list_filter   = ['type_action']
    search_fields = ['utilisateur__username', 'restaurant__nom']
    readonly_fields = ['created_at']
    date_hierarchy  = 'created_at'


@admin.register(CacheRecommandation)
class CacheRecoAdmin(admin.ModelAdmin):
    list_display    = ['utilisateur', 'nb_ids', 'calculee_le']
    readonly_fields = ['calculee_le']
    search_fields   = ['utilisateur__username']

    def nb_ids(self, obj):
        return len(obj.restaurant_ids)
    nb_ids.short_description = 'Nb recommandations'
