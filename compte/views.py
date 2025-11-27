from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import InscriptionForm
from django.views.generic import TemplateView


class InscriptionView(CreateView):
    form_class = InscriptionForm
    template_name = "compte/inscription.html"
    success_url = reverse_lazy("depense_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Compte créé. Bienvenue !")
        return response

class AccueilView(TemplateView):
    template_name = "compte/accueil.html"