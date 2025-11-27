from django import forms
from .models import Budget, Depense
from decimal import Decimal

class DateInput(forms.DateInput):
    input_type = "date"

class MoneyInput(forms.NumberInput):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {}).update({"step": "0.01"})
        super().__init__(*args, **kwargs)

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["libelle", "date_debut", "date_fin", "montant_budget"]
        widgets = {
            "libelle": forms.TextInput(attrs={"class": "w-full rounded border px-3 py-2"}),
            "date_debut": DateInput(attrs={"class": "w-full rounded border px-3 py-2"}),
            "date_fin": DateInput(attrs={"class": "w-full rounded border px-3 py-2"}),
            "montant_budget": MoneyInput(attrs={"class": "w-full rounded border px-3 py-2"}),
        }

    def clean(self):
        data = super().clean()
        dd = data.get("date_debut")
        df = data.get("date_fin")
        if dd and df and df < dd:
            self.add_error("date_fin", "La date de fin ne peut pas être avant la date de début.")
        mb = data.get("montant_budget")
        if mb is not None and mb < Decimal("0"):
            self.add_error("montant_budget", "Le montant du budget doit être positif.")
        return data


class DepenseForm(forms.ModelForm):
    class Meta:
        model = Depense
        fields = ["date_depense", "objet", "montant", "budget"]
        widgets = {
            "date_depense": DateInput(attrs={"class": "w-full rounded border px-3 py-2"}),
            "objet": forms.TextInput(attrs={"class": "w-full rounded border px-3 py-2"}),
            "montant": MoneyInput(attrs={"class": "w-full rounded border px-3 py-2"}),
            "budget": forms.Select(attrs={"class": "w-full rounded border px-3 py-2"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["budget"].queryset = user.budgets.all()
