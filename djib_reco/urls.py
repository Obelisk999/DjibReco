from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from restaurants.views import accueil, dashboard_utilisateur

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', accueil, name='accueil'),
    path('dashboard/', dashboard_utilisateur, name='dashboard_utilisateur'),
    path('restaurants/', include('restaurants.urls')),
    path('accounts/', include('accounts.urls')),
    path('recommandations/', include('recommandation.urls')),  # ← ajouter
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
