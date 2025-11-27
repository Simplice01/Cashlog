from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class InscriptionForm(UserCreationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        "class": "w-full rounded border px-3 py-2"
    }))
    nom = forms.CharField(label="Nom", max_length=120, widget=forms.TextInput(attrs={
        "class": "w-full rounded border px-3 py-2"
    }))
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={
        "class": "w-full rounded border px-3 py-2"
    }))
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={
        "class": "w-full rounded border px-3 py-2"
    }))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "nom")

class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        "class": "w-full rounded border px-3 py-2"
    }))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={
        "class": "w-full rounded border px-3 py-2"
    }))
