from django.contrib import admin
from django.urls import path, include
from depenses.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Accueil à la racine
    path("", home, name="home"),

    # Apps
    path('', include('depenses.urls')),
    path('', include('compte.urls')),
]
