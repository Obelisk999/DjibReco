# 📋 PLAN D'ACTION - Corrections à Appliquer

**Priorité**: 🔴 URGENT → 🟠 IMPORTANT → 🟡 SOUHAITABLE

---

## 🔴 URGENT - 48 heures

### 1. FIX: Exceptions vagues dans `hybrid_engine.py`

**Fichier**: `recommandation/hybrid_engine.py` (ligne ~163)

**Avant**: 
```python
except:
    return contexte_cache.get('default', {})
```

**Après**:
```python
except Exception as e:
    logger.warning(f"[HybridEngine] Erreur fetch cache: {e}")
    return contexte_cache.get('default', {})
```

---

### 2. FIX: Exceptions vagues dans `admin.py`

**Fichier**: `recommandation/admin.py` (ligne ~121)

**Avant**:
```python
except:
    return format_html(...)
```

**Après**:
```python
except (ValueError, TypeError) as e:  # Exceptions spécifiques attendues
    logger.info(f"[RecoAdmin] Format invalide: {e}")
    return format_html(...)
```

---

### 3. FIX: Ajouter `@staff_required` aux routes sensibles

**Fichier**: `restaurants/views.py`

**Ajouter le décorateur à**:
- Ligne 354: `ajouter_restaurant()`
- Ligne 370: `modifier_restaurant()`
- Ligne 384: `ajouter_menu_item()`
- Ligne 402: `supprimer_menu_item()`

**Avant**:
```python
def ajouter_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.ajoute_par = request.user
            restaurant.save()
            return redirect('liste_restaurants')
```

**Après**:
```python
@login_required
@staff_required
def ajouter_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.ajoute_par = request.user
            restaurant.save()
            return redirect('liste_restaurants')
```

---

## 🟠 IMPORTANT - Avant production (1 semaine)

### 4. FIX: Requêtes N+1 dans `detail_restaurant()`

**Fichier**: `restaurants/views.py` (lignes 128-135)

**Problème**:
```python
plats = restaurant.menu_items.filter(type_item='plat', disponible=True)
boissons = restaurant.menu_items.filter(type_item='boisson', disponible=True)
cafes = restaurant.menu_items.filter(type_item='cafe', disponible=True)
# = 3 requêtes SQL séparées
```

**Solution**:
```python
# Option 1: Une seule query
menu_disponible = restaurant.menu_items.filter(disponible=True)
plats = [m for m in menu_disponible if m.type_item == 'plat']
boissons = [m for m in menu_disponible if m.type_item == 'boisson']
cafes = [m for m in menu_disponible if m.type_item == 'cafe']

# Option 2: Avec annotation (plus élégant)
from django.db.models import Case, When, Value, CharField

items = restaurant.menu_items.filter(disponible=True).values('type_item')
plats = [m for m in items if m['type_item'] == 'plat']
```

---

### 5. FIX: COUNT redondants dans `dashboard_utilisateur()`

**Fichier**: `restaurants/views.py` (lignes ~261-263)

**Avant**:
```python
context = {
    'user': user,
    'favoris': favoris,
    'mes_avis': mes_avis,
    'restaurants_ajoutes': restaurants_ajoutes,
    'nb_favoris': Favori.objects.filter(utilisateur=user).count(),     # Requête séparée
    'nb_avis': Avis.objects.filter(utilisateur=user).count(),           # Requête séparée
    'nb_restaurants': Restaurant.objects.filter(ajoute_par=user).count(), # Requête séparée
}
```

**Après**:
```python
context = {
    'user': user,
    'favoris': favoris,
    'mes_avis': mes_avis,
    'restaurants_ajoutes': restaurants_ajoutes,
    'nb_favoris': len(favoris),                      # ✅ Pas de requête 
    'nb_avis': len(mes_avis),                        # ✅ Pas de requête
    'nb_restaurants': len(restaurants_ajoutes),      # ✅ Pas de requête
}
```

---

### 6. FIX: Validation du paramètre `nb` dans les endpoints

**Fichier**: `recommandation/views.py`

**Localisation**: Lignes 58, 230, 318

**Avant**:
```python
def collaborative_based_view(request):
    reco_id = request.GET.get('restaurant_id')
    nb = int(request.GET.get('nb', 6))  # ❌ Pas de limite
```

**Après**:
```python
def collaborative_based_view(request):
    reco_id = request.GET.get('restaurant_id')
    try:
        nb = int(request.GET.get('nb', 6))
        nb = min(max(1, nb), 100)  # ✅ Limiter à [1, 100]
    except TypeError:
        nb = 6
```

---

## 🟡 SOUHAITABLE - Amélioration continue

### 7. OPT: Limitation et validation du paramètre `alpha`

**Fichier**: `recommandation/views.py` (ligne 269)

**Avant**:
```python
alpha = float(request.GET.get('alpha', 0.6))
```

**Après**:
```python
try:
    alpha = float(request.GET.get('alpha', 0.6))
    alpha = max(0.0, min(1.0, alpha))  # ✅ Limiter à [0.0, 1.0]
except (ValueError, TypeError):
    alpha = 0.6
```

---

### 8. OPT: Refactorisation boucle inefficace dans `detail_restaurant()`

**Fichier**: `restaurants/views.py` (lignes 153-157)

**Avant**:
```python
similaires_content = []
for r in reco_content:
    if len(similaires_collab) + len(similaires_content) >= NB_CIBLE:
        break
    similaires_content.append(r)
```

**Après**:
```python
remaining = max(0, NB_CIBLE - len(similaires_collab))
similaires_content = reco_content[:remaining]
```

---

### 9. OPT: Pagination sur `liste_restaurants()`

**Fichier**: `restaurants/views.py`

**Avant**:
```python
restaurants = restaurants.annotate(...).order_by(tri)
context['restaurants'] = restaurants  # ❌ Pas de pagination
```

**Après**:
```python
from django.core.paginator import Paginator

restaurants = restaurants.annotate(...).order_by(tri)
paginator = Paginator(restaurants, 20)  # 20 restaurants par page
page = paginator.get_page(request.GET.get('page', 1))
context['restaurants'] = page
```

Et dans le template:
```django
<!-- Navbartion paginage -->
{% if page.has_other_pages %}
  <nav>
    {% if page.has_previous %}
      <a href="?page=1">Première</a>
      <a href="?page={{ page.previous_page_number }}">Précédente</a>
    {% endif %}
    
    <span>Page {{ page.number }} sur {{ page.paginator.num_pages }}</span>
    
    {% if page.has_next %}
      <a href="?page={{ page.next_page_number }}">Suivante</a>
      <a href="?page={{ page.paginator.num_pages }}">Dernière</a>
    {% endif %}
  </nav>
{% endif %}
```

---

### 10. OPT: Validation de taille d'image

**Fichier**: `restaurants/forms.py` OU `restaurants/models.py`

**Ajouter dans les modèles**:
```python
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class MenuItem(models.Model):
    image = models.ImageField(
        upload_to='menu/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    
    def clean(self):
        if self.image:
            if self.image.size > 5 * 1024 * 1024:  # 5MB limite
                raise ValidationError({'image': 'L\'image ne doit pas dépasser 5MB'})
```

---

### 11. OPT: Extension cache invalidation

**Fichier**: `recommandation/signals.py`

**À ajouter**:
```python
from django.db.models.signals import post_save
from restaurants.models import Restaurant

@receiver(post_save, sender=Restaurant)
def invalider_cache_restaurant_change(sender, instance, **kwargs):
    """Invalider cache si la catégorie/gamme_prix d'un restaurant change"""
    _invalider_cache()  # Cache global

# À enregistrer dans apps.py:
default_app_config = 'recommandation.apps.RecommandationConfig'
```

---

### 12. OPT: Ajouter docstrings aux modèles

**Exemple pour `MenuItem`**:
```python
class MenuItem(models.Model):
    """
    Représente un article de menu d'un restaurant.
    
    Attributs:
        restaurant: Référence au restaurant propriétaire
        nom: Nom du plat/boisson
        prix: Prix en DJF
        type_item: 'plat', 'boisson', ou 'cafe'
        image: Image optionnelle du menu
        disponible: Si actuellement offert
    """
    restaurant = models.ForeignKey(...)
    ...
```

---

## 📊 Tableau de Déploiement

| # | Titre | Fichier | Urgence | Effort | Status |
|---|-------|---------|---------|--------|--------|
| 1 | Exceptions vagues - hybrid_engine.py | recommandation/hybrid_engine.py | 🔴 | 5min | ⏳ |
| 2 | Exceptions vagues - admin.py | recommandation/admin.py | 🔴 | 5min | ⏳ |
| 3 | @staff_required manquant | restaurants/views.py | 🔴 | 10min | ⏳ |
| 4 | Requêtes N+1 | restaurants/views.py | 🟠 | 20min | ⏳ |
| 5 | COUNT redondants | restaurants/views.py | 🟠 | 10min | ⏳ |
| 6 | Paramètre nb sans limite | recommandation/views.py | 🟠 | 15min | ⏳ |
| 7 | Paramètre alpha sans limite | recommandation/views.py | 🟡 | 10min | ⏳ |
| 8 | Boucle inefficace | restaurants/views.py | 🟡 | 10min | ⏳ |
| 9 | Pagination manquante | restaurants/views.py | 🟡 | 30min | ⏳ |
| 10 | Validation image | restaurants/models.py | 🟡 | 20min | ⏳ |
| 11 | Cache extension | recommandation/signals.py | 🟡 | 15min | ⏳ |
| 12 | Docstrings | Tous les modèles | 🟡 | 30min | ⏳ |

**Estimation temps total**: 3-4 heures (si tout appliqué)

---

## ✅ Checklist de Test après corrections

- [ ] `python manage.py test` → 68/68 passing  
- [ ] Test unauthorized access à `/restaurants/ajouter/`  
- [ ] Test image validation (>5MB)  
- [ ] Test parameter limits (`?nb=10000`, `?alpha=2.5`)  
- [ ] Load test avec pagination  
- [ ] Vérifier requêtes SQL avec `django-debug-toolbar`  

---

## 📌 Priorité Immédiate

**FAIRE EN PREMIER (30 minutes)**:
1. Fix exceptions vagues (items 1-2)
2. Ajouter @staff_required (item 3)
3. Valider paramètres (item 6)

Cela résout 80% des problèmes critiques en 30 minutes de travail.
