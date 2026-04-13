"""
recommandation/admin.py
Interface d'administration pour le système de recommandation.

Permet de monitorer:
  - InteractionUtilisateur: vues, clics, partages
  - CacheRecommandation: cache des recommandations
  - Analyse: quel algorithme est utilisé pour chaque utilisateur
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import InteractionUtilisateur, CacheRecommandation
from .hybrid_engine import analyser_couverture_algorithme


@admin.register(InteractionUtilisateur)
class InteractionAdmin(admin.ModelAdmin):
    """Admin pour les interactions implicites (vues, clics, partages)."""
    
    list_display  = ['utilisateur', 'restaurant', 'type_action_color', 'score', 'created_at']
    list_filter   = ['type_action', 'created_at']
    search_fields = ['utilisateur__username', 'restaurant__nom']
    readonly_fields = ['created_at', 'type_action_detail']
    date_hierarchy  = 'created_at'
    ordering = ['-created_at']

    def type_action_color(self, obj):
        """Affiche le type d'action avec une couleur."""
        colors = {
            'vue': '#1f77b4',      # Bleu
            'clic_menu': '#ff7f0e', # Orange
            'partage': '#2ca02c',   # Vert
        }
        color = colors.get(obj.type_action, '#7f7f7f')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_type_action_display()
        )
    type_action_color.short_description = 'Type d\'action'

    def type_action_detail(self, obj):
        """Détail du type d'action."""
        types = {
            'vue': '👀 Utilisateur a consulté le restaurant',
            'clic_menu': '📋 Utilisateur a cliqué sur le menu',
            'partage': '🔗 Utilisateur a partagé le restaurant',
        }
        return types.get(obj.type_action, obj.type_action)
    type_action_detail.short_description = 'Détail'


@admin.register(CacheRecommandation)
class CacheRecoAdmin(admin.ModelAdmin):
    """Admin pour le cache des recommandations."""
    
    list_display    = ['utilisateur', 'nb_ids_display', 'age_cache', 'status_algo']
    readonly_fields = ['calculee_le', 'restaurant_ids_list', 'couverture_detail']
    search_fields   = ['utilisateur__username']
    ordering = ['-calculee_le']

    def nb_ids_display(self, obj):
        """Affiche le nombre de recommandations avec une couleur."""
        count = len(obj.restaurant_ids) if obj.restaurant_ids else 0
        if count == 0:
            color = '#d62728'  # Rouge
        elif count < 3:
            color = '#ff7f0e'  # Orange
        else:
            color = '#2ca02c'  # Vert
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            count
        )
    nb_ids_display.short_description = 'Nb recos'

    def age_cache(self, obj):
        """Affiche l'âge du cache."""
        from django.utils import timezone
        from datetime import timedelta
        
        age = timezone.now() - obj.calculee_le
        ttl = timedelta(hours=1)
        
        if age < ttl:
            color = '#2ca02c'  # Vert (cache frais)
            status = f'✅ Frais ({age.seconds}s)'
        else:
            color = '#d62728'  # Rouge (cache expiré)
            status = f'⚠️ Expiré ({age.total_seconds()/3600:.1f}h)'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            status
        )
    age_cache.short_description = 'État cache'

    def status_algo(self, obj):
        """Affiche quel algorithme peut servir cet utilisateur."""
        try:
            couverture = analyser_couverture_algorithme(obj.utilisateur_id)
            status_map = {
                'cold_start': ('❄️ Cold-start', '#1f77b4'),
                'warm_cb': ('📊 CB seulement', '#ff7f0e'),
                'warm_cf': ('👥 CF/Hybride', '#2ca02c'),
                'error': ('❌ Erreur', '#d62728'),
            }
            status_text, color = status_map.get(
                couverture['recommendation_status'],
                ('❓ Inconnu', '#7f7f7f')
            )
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                status_text
            )
        except:
            return format_html(
                '<span style="color: #d62728; font-weight: bold;">❌ Erreur</span>'
            )
    status_algo.short_description = 'Algorithme'

    def restaurant_ids_list(self, obj):
        """Affiche la liste des IDs recommandés."""
        ids = obj.restaurant_ids or []
        return ', '.join(map(str, ids[:6])) + ('...' if len(ids) > 6 else '')
    restaurant_ids_list.short_description = 'IDs recommandés'

    def couverture_detail(self, obj):
        """Analyse complète de couverture."""
        try:
            couverture = analyser_couverture_algorithme(obj.utilisateur_id)
            return format_html(
                '<table style="border-collapse: collapse; width: 100%;">'
                '<tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>CF disponible</strong></td>'
                '<td style="padding: 5px; border: 1px solid #ddd;">{}</td></tr>'
                '<tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>CB disponible</strong></td>'
                '<td style="padding: 5px; border: 1px solid #ddd;">{}</td></tr>'
                '<tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Interactions</strong></td>'
                '<td style="padding: 5px; border: 1px solid #ddd;">{}</td></tr>'
                '<tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Avis donnés</strong></td>'
                '<td style="padding: 5px; border: 1px solid #ddd;">{}</td></tr>'
                '<tr><td style="padding: 5px; border: 1px solid #ddd;"><strong>Status</strong></td>'
                '<td style="padding: 5px; border: 1px solid #ddd;">{}</td></tr>'
                '</table>',
                '✅' if couverture['used_cf'] else '❌',
                '✅' if couverture['used_cb'] else '❌',
                couverture['interaction_count'],
                couverture['avis_count'],
                couverture['recommendation_status'].upper(),
            )
        except Exception as e:
            return f'Erreur: {str(e)}'
    couverture_detail.short_description = 'Analyse de couverture'

