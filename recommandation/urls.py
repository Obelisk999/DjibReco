"""
recommandation/urls.py
"""
from django.urls import path
from . import views

app_name = 'recommandation'

urlpatterns = [
    # Recommandations personnalisées (JSON)
    path(
        'pour-moi/',
        views.recommandations_pour_moi,
        name='pour_moi'
    ),
    # Enregistrement interaction implicite (AJAX POST)
    path(
        'interaction/',
        views.enregistrer_interaction_view,
        name='interaction'
    ),
    # Restaurants similaires (JSON)
    path(
        'similaires/<slug:slug>/',
        views.restaurants_similaires_view,
        name='similaires'
    ),
]
