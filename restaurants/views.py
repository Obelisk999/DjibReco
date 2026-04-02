from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Avg, Q, Count
from django.http import JsonResponse
from .models import Restaurant, Categorie, MenuItem, Avis, Favori
from .forms import RestaurantForm, MenuItemForm, AvisForm


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_staff, login_url='/accounts/connexion/')(view_func)


# ─── PUBLIC ───────────────────────────────────────────────────────────────────

def accueil(request):
    categories = Categorie.objects.annotate(nb=Count('restaurants')).order_by('-nb')
    restaurants_vedettes = Restaurant.objects.filter(est_vedette=True, est_ouvert=True).annotate(
        note_avg=Avg('avis__note')
    )[:6]
    top_restaurants = Restaurant.objects.annotate(
        note_avg=Avg('avis__note'), nb_avis=Count('avis')
    ).filter(est_ouvert=True, nb_avis__gt=0).order_by('-note_avg')[:6]
    restaurants_recents = Restaurant.objects.filter(est_ouvert=True).annotate(
        note_avg=Avg('avis__note')
    ).order_by('-date_creation')[:8]

    # IDs des favoris de l'utilisateur
    favoris_ids = set()
    if request.user.is_authenticated:
        favoris_ids = set(Favori.objects.filter(utilisateur=request.user).values_list('restaurant_id', flat=True))

    return render(request, 'restaurants/accueil.html', {
        'categories': categories,
        'restaurants_vedettes': restaurants_vedettes,
        'top_restaurants': top_restaurants,
        'restaurants_recents': restaurants_recents,
        'favoris_ids': favoris_ids,
        'total_restaurants': Restaurant.objects.count(),
        'total_categories': categories.count(),
    })


def liste_restaurants(request):
    restaurants = Restaurant.objects.annotate(note_avg=Avg('avis__note'), nb_avis=Count('avis'))
    categories = Categorie.objects.all()

    categorie_slug = request.GET.get('categorie', '')
    recherche = request.GET.get('q', '')
    budget = request.GET.get('budget', '')
    ouvert = request.GET.get('ouvert', '')
    tri = request.GET.get('tri', '-date_creation')

    if categorie_slug:
        restaurants = restaurants.filter(categorie__slug=categorie_slug)
    if recherche:
        restaurants = restaurants.filter(
            Q(nom__icontains=recherche) | Q(adresse__icontains=recherche) |
            Q(description__icontains=recherche) | Q(categorie__nom__icontains=recherche)
        )
    if budget in ['$', '$$', '$$$']:
        restaurants = restaurants.filter(gamme_prix=budget)
    if ouvert:
        restaurants = restaurants.filter(est_ouvert=True)
    if tri in ['-date_creation', 'nom', '-note_avg', '-nb_avis']:
        restaurants = restaurants.order_by(tri)

    favoris_ids = set()
    if request.user.is_authenticated:
        favoris_ids = set(Favori.objects.filter(utilisateur=request.user).values_list('restaurant_id', flat=True))

    return render(request, 'restaurants/liste.html', {
        'restaurants': restaurants,
        'categories': categories,
        'categorie_active': categorie_slug,
        'recherche': recherche,
        'budget': budget,
        'tri': tri,
        'favoris_ids': favoris_ids,
        'total': restaurants.count(),
    })


def detail_restaurant(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    plats = restaurant.menu_items.filter(type_item='plat', disponible=True)
    boissons = restaurant.menu_items.filter(type_item='boisson', disponible=True)
    cafes = restaurant.menu_items.filter(type_item='cafe', disponible=True)
    avis_liste = restaurant.avis.select_related('utilisateur').all()

    utilisateur_a_deja_note = False
    avis_form = None
    est_favori = False

    if request.user.is_authenticated:
        utilisateur_a_deja_note = Avis.objects.filter(utilisateur=request.user, restaurant=restaurant).exists()
        est_favori = Favori.objects.filter(utilisateur=request.user, restaurant=restaurant).exists()
        if not utilisateur_a_deja_note:
            avis_form = AvisForm()

    if request.method == 'POST' and request.user.is_authenticated and not utilisateur_a_deja_note:
        avis_form = AvisForm(request.POST)
        if avis_form.is_valid():
            avis = avis_form.save(commit=False)
            avis.utilisateur = request.user
            avis.restaurant = restaurant
            avis.save()
            messages.success(request, 'Votre avis a été publié !')
            return redirect('detail_restaurant', slug=slug)

    # Restaurants similaires
    similaires = Restaurant.objects.filter(
        categorie=restaurant.categorie, est_ouvert=True
    ).exclude(pk=restaurant.pk).annotate(note_avg=Avg('avis__note'))[:3]

    return render(request, 'restaurants/detail.html', {
        'restaurant': restaurant,
        'plats': plats,
        'boissons': boissons,
        'cafes': cafes,
        'avis_liste': avis_liste,
        'avis_form': avis_form,
        'utilisateur_a_deja_note': utilisateur_a_deja_note,
        'est_favori': est_favori,
        'note_moyenne': restaurant.note_moyenne(),
        'nombre_avis': restaurant.nombre_avis(),
        'similaires': similaires,
    })


def recherche(request):
    q = request.GET.get('q', '')
    restaurants = []
    if q:
        restaurants = Restaurant.objects.filter(
            Q(nom__icontains=q) | Q(adresse__icontains=q) |
            Q(description__icontains=q) | Q(categorie__nom__icontains=q)
        ).annotate(note_avg=Avg('avis__note'))
    return render(request, 'restaurants/recherche.html', {'restaurants': restaurants, 'query': q})


# ─── UTILISATEUR CONNECTÉ ─────────────────────────────────────────────────────

@login_required
def dashboard_utilisateur(request):
    user = request.user
    favoris = Favori.objects.filter(utilisateur=user).select_related('restaurant__categorie')[:6]
    mes_avis = Avis.objects.filter(utilisateur=user).select_related('restaurant')[:5]
    restaurants_ajoutes = Restaurant.objects.filter(ajoute_par=user).annotate(
        note_avg=Avg('avis__note')
    )[:5]

    # Recommandations personnalisées
    categories_aimees = Avis.objects.filter(
        utilisateur=user, note__gte=4
    ).values_list('restaurant__categorie_id', flat=True).distinct()
    restaurants_notes_ids = Avis.objects.filter(utilisateur=user).values_list('restaurant_id', flat=True)
    recommandations = Restaurant.objects.filter(
        categorie__in=categories_aimees, est_ouvert=True
    ).exclude(id__in=restaurants_notes_ids).annotate(
        note_avg=Avg('avis__note')
    ).order_by('-note_avg')[:6]

    if not recommandations.exists():
        recommandations = Restaurant.objects.exclude(
            id__in=restaurants_notes_ids
        ).annotate(note_avg=Avg('avis__note')).order_by('-note_avg')[:6]

    return render(request, 'restaurants/dashboard.html', {
        'favoris': favoris,
        'mes_avis': mes_avis,
        'restaurants_ajoutes': restaurants_ajoutes,
        'recommandations': recommandations,
        'nb_favoris': Favori.objects.filter(utilisateur=user).count(),
        'nb_avis': Avis.objects.filter(utilisateur=user).count(),
        'nb_restaurants': Restaurant.objects.filter(ajoute_par=user).count(),
    })


@login_required
def toggle_favori(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    favori, created = Favori.objects.get_or_create(utilisateur=request.user, restaurant=restaurant)
    if not created:
        favori.delete()
        est_favori = False
        msg = f'"{restaurant.nom}" retiré de vos favoris.'
    else:
        est_favori = True
        msg = f'"{restaurant.nom}" ajouté à vos favoris !'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'est_favori': est_favori, 'message': msg})
    messages.success(request, msg)
    return redirect('detail_restaurant', slug=slug)


@login_required
def supprimer_avis(request, avis_id):
    avis = get_object_or_404(Avis, id=avis_id)
    if avis.utilisateur != request.user and not request.user.is_staff:
        messages.error(request, "Vous ne pouvez pas supprimer cet avis.")
        return redirect('detail_restaurant', slug=avis.restaurant.slug)
    slug = avis.restaurant.slug
    avis.delete()
    messages.success(request, 'Avis supprimé.')
    return redirect('detail_restaurant', slug=slug)


# ─── ADMIN UNIQUEMENT ─────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('accueil')

    from django.contrib.auth.models import User as UserModel
    total_restaurants = Restaurant.objects.count()
    total_users = UserModel.objects.count()
    total_avis = Avis.objects.count()
    total_menu = MenuItem.objects.count()
    top_restaurants = Restaurant.objects.annotate(
        note_avg=Avg('avis__note'), nb_avis=Count('avis')
    ).order_by('-note_avg')[:5]
    recents = Restaurant.objects.order_by('-date_creation')[:5]
    derniers_avis = Avis.objects.select_related('utilisateur', 'restaurant').order_by('-date_creation')[:5]
    stats_cat = Categorie.objects.annotate(nb=Count('restaurants')).order_by('-nb')

    return render(request, 'restaurants/admin_dashboard.html', {
        'total_restaurants': total_restaurants,
        'total_users': total_users,
        'total_avis': total_avis,
        'total_menu': total_menu,
        'top_restaurants': top_restaurants,
        'recents': recents,
        'derniers_avis': derniers_avis,
        'stats_cat': stats_cat,
    })


@staff_required
def ajouter_restaurant(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.ajoute_par = request.user
            restaurant.save()
            messages.success(request, f'"{restaurant.nom}" ajouté avec succès !')
            return redirect('detail_restaurant', slug=restaurant.slug)
    else:
        form = RestaurantForm()
    return render(request, 'restaurants/ajouter_restaurant.html', {'form': form})


@staff_required
def modifier_restaurant(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, request.FILES, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Restaurant mis à jour !')
            return redirect('detail_restaurant', slug=restaurant.slug)
    else:
        form = RestaurantForm(instance=restaurant)
    return render(request, 'restaurants/modifier_restaurant.html', {'form': form, 'restaurant': restaurant})


@staff_required
def ajouter_menu_item(request, slug):
    restaurant = get_object_or_404(Restaurant, slug=slug)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.restaurant = restaurant
            item.save()
            messages.success(request, f'"{item.nom}" ajouté au menu !')
            return redirect('detail_restaurant', slug=slug)
    else:
        form = MenuItemForm()
    return render(request, 'restaurants/ajouter_menu.html', {'form': form, 'restaurant': restaurant})


@staff_required
def supprimer_menu_item(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    slug = item.restaurant.slug
    nom = item.nom
    item.delete()
    messages.success(request, f'"{nom}" supprimé du menu.')
    return redirect('detail_restaurant', slug=slug)
