from django.shortcuts import render

# Create your views here.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.dateparse import parse_date

from .models import Budget, Depense
from .forms import BudgetForm, DepenseForm

# ========= BUDGETS =========

class BudgetListeView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = "depenses/budget_liste.html"
    context_object_name = "budgets"

    def get_queryset(self):
        return Budget.objects.filter(utilisateur=self.request.user).order_by("-date_debut", "-id")


class BudgetCreerView(LoginRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "depenses/budget_form.html"
    success_url = reverse_lazy("budget_list")

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        messages.success(self.request, "Budget créé avec succès.")
        return super().form_valid(form)


class BudgetModifierView(LoginRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = "depenses/budget_form.html"
    success_url = reverse_lazy("budget_list")

    def get_queryset(self):
        return Budget.objects.filter(utilisateur=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Budget modifié avec succès.")
        return super().form_valid(form)


class BudgetSupprimerView(LoginRequiredMixin, DeleteView):
    model = Budget
    template_name = "depenses/confirm_delete.html"
    success_url = reverse_lazy("budget_list")

    def get_queryset(self):
        return Budget.objects.filter(utilisateur=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Budget supprimé.")
        return super().delete(request, *args, **kwargs)


# ========= DEPENSES =========

class DepenseListeView(LoginRequiredMixin, ListView):
    model = Depense
    template_name = "depenses/depense_liste.html"
    context_object_name = "depenses"

    def get_queryset(self):
        qs = Depense.objects.select_related("budget").filter(utilisateur=self.request.user)
        # Filtres GET ?date=YYYY-MM-DD ou ?debut=...&fin=...&budget=ID
        jour = self.request.GET.get("date")
        debut = self.request.GET.get("debut")
        fin = self.request.GET.get("fin")
        budget_id = self.request.GET.get("budget")

        if jour:
            d = parse_date(jour)
            if d:
                qs = qs.filter(date_depense=d)
        else:
            if debut:
                d1 = parse_date(debut)
                if d1:
                    qs = qs.filter(date_depense__gte=d1)
            if fin:
                d2 = parse_date(fin)
                if d2:
                    qs = qs.filter(date_depense__lte=d2)
        if budget_id:
            qs = qs.filter(budget_id=budget_id)

        return qs.order_by("-date_depense", "-id")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["budgets"] = Budget.objects.filter(utilisateur=self.request.user).order_by("-date_debut")
        ctx["val_date"] = self.request.GET.get("date", "")
        ctx["val_debut"] = self.request.GET.get("debut", "")
        ctx["val_fin"] = self.request.GET.get("fin", "")
        ctx["val_budget"] = self.request.GET.get("budget", "")
        # Totaux utiles
        ctx["total"] = sum(d.montant for d in ctx["depenses"])
        return ctx


class DepenseCreerView(LoginRequiredMixin, CreateView):
    model = Depense
    form_class = DepenseForm
    template_name = "depenses/depense_form.html"
    success_url = reverse_lazy("depense_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # restreint la liste des budgets
        return kwargs

    def form_valid(self, form):
        form.instance.utilisateur = self.request.user
        messages.success(self.request, "Dépense ajoutée avec succès.")
        return super().form_valid(form)


class DepenseModifierView(LoginRequiredMixin, UpdateView):
    model = Depense
    form_class = DepenseForm
    template_name = "depenses/depense_form.html"
    success_url = reverse_lazy("depense_list")

    def get_queryset(self):
        return Depense.objects.filter(utilisateur=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Dépense modifiée avec succès.")
        return super().form_valid(form)


class DepenseSupprimerView(LoginRequiredMixin, DeleteView):
    model = Depense
    template_name = "depenses/confirm_delete.html"
    success_url = reverse_lazy("depense_list")

    def get_queryset(self):
        return Depense.objects.filter(utilisateur=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Dépense supprimée.")
        return super().delete(request, *args, **kwargs)
    
from django.views.generic import TemplateView

class AccueilView(TemplateView):
    template_name = "accueil.html"
    
class HomeView(TemplateView):
    template_name = "depenses/home.html"    


def home(request):
    return render(request, 'home.html')