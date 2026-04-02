from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_restaurants, name='liste_restaurants'),
    path('ajouter/', views.ajouter_restaurant, name='ajouter_restaurant'),
    path('recherche/', views.recherche, name='recherche'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('<slug:slug>/', views.detail_restaurant, name='detail_restaurant'),
    path('<slug:slug>/modifier/', views.modifier_restaurant, name='modifier_restaurant'),
    path('<slug:slug>/menu/ajouter/', views.ajouter_menu_item, name='ajouter_menu_item'),
    path('<slug:slug>/favori/', views.toggle_favori, name='toggle_favori'),
    path('avis/<int:avis_id>/supprimer/', views.supprimer_avis, name='supprimer_avis'),
    path('menu/<int:item_id>/supprimer/', views.supprimer_menu_item, name='supprimer_menu_item'),
]
