from django.urls import path
from django.contrib.auth import views as auth_views
from .views import InscriptionView
from .forms import ConnexionForm
from django.urls import path, include
from .views import AccueilView




urlpatterns = [
    path("inscription/", InscriptionView.as_view(), name="signup"),
    path("connexion/", auth_views.LoginView.as_view(
        template_name="compte/connexion.html",
        authentication_form=ConnexionForm
    ), name="login"),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("depenses.urls")), 
    path("", AccueilView.as_view(), name="home"),  # ← la page d’accueil

]
# compte/urls.py
