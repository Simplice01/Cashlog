from django.urls import path
from .views_chat import AssistantView
from .views import (
    BudgetListeView, BudgetCreerView, BudgetModifierView, BudgetSupprimerView,
    DepenseListeView, DepenseCreerView, DepenseModifierView, DepenseSupprimerView, AccueilView,
)

urlpatterns = [



    # Budgets
    path("budgets/", BudgetListeView.as_view(), name="budget_list"),
    path("budgets/ajouter/", BudgetCreerView.as_view(), name="budget_add"),
    path("budgets/<int:pk>/modifier/", BudgetModifierView.as_view(), name="budget_edit"),
    path("budgets/<int:pk>/supprimer/", BudgetSupprimerView.as_view(), name="budget_delete"),

    # Dépenses
    path("depenses/", DepenseListeView.as_view(), name="depense_list"),
    path("depenses/ajouter/", DepenseCreerView.as_view(), name="depense_add"),
    path("depenses/<int:pk>/modifier/", DepenseModifierView.as_view(), name="depense_edit"),
    path("depenses/<int:pk>/supprimer/", DepenseSupprimerView.as_view(), name="depense_delete"),

    path('', AccueilView.as_view(), name='home'),
    path("assistant/", AssistantView.as_view(), name="assistant"),
    

    # budgets/

]

