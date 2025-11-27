
# Register your models here.
from django.contrib import admin
from .models import Budget, Depense

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("libelle", "utilisateur", "date_debut", "date_fin", "montant_budget", "total_depense", "restant", "statut")
    list_filter = ("date_debut", "date_fin")
    search_fields = ("libelle", "utilisateur__email", "utilisateur__nom")
    ordering = ("-date_debut", "-id")

    # Limite la vue à ses propres données dans l’admin (optionnel)
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(utilisateur=request.user)

    # Renseigne automatiquement l’utilisateur sur création via admin
    def save_model(self, request, obj, form, change):
        if not change or obj.utilisateur_id is None:
            obj.utilisateur = request.user
        super().save_model(request, obj, form, change)


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ("date_depense", "objet", "montant", "utilisateur", "budget")
    list_filter = ("date_depense", "budget")
    search_fields = ("objet", "utilisateur__email", "utilisateur__nom")
    ordering = ("-date_depense", "-id")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(utilisateur=request.user)

    def save_model(self, request, obj, form, change):
        if not change or obj.utilisateur_id is None:
            obj.utilisateur = request.user
        super().save_model(request, obj, form, change)
