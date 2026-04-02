from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm


def inscription(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé.')
            return redirect('accueil')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/inscription.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Bon retour, {user.first_name or user.username} !')
            next_url = request.GET.get('next', 'accueil')
            return redirect(next_url)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ConnexionForm(request)
    return render(request, 'accounts/connexion.html', {'form': form})


@login_required
def deconnexion(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('accueil')


@login_required
def profil(request):
    restaurants_ajoutes = request.user.restaurants_ajoutes.all()[:5]
    avis_donnes = request.user.avis.select_related('restaurant').all()[:5]
    context = {
        'restaurants_ajoutes': restaurants_ajoutes,
        'avis_donnes': avis_donnes,
    }
    return render(request, 'accounts/profil.html', context)
