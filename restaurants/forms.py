from django import forms
from .models import Restaurant, MenuItem, Avis


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['nom', 'description', 'adresse', 'telephone', 'categorie',
                  'image', 'cover_url', 'horaires', 'site_web', 'gamme_prix', 'est_ouvert', 'est_vedette']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du restaurant'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Plateau du Serpent, Djibouti'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+253 77 XX XX XX'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://images.unsplash.com/...'}),
            'horaires': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lun-Dim 7h-22h'}),
            'site_web': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'gamme_prix': forms.Select(attrs={'class': 'form-select'}),
            'est_ouvert': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_vedette': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['nom', 'description', 'prix', 'type_item', 'image', 'cover_url', 'disponible']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du plat/boisson'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'prix': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Prix en FDJ'}),
            'type_item': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AvisForm(forms.ModelForm):
    class Meta:
        model = Avis
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.HiddenInput(),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Partagez votre expérience...'
            }),
        }
