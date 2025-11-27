from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum, F, Q


class Budget(models.Model):
    # 🔗 Propriétaire du budget
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="budgets",
        verbose_name="Utilisateur",
    )

    libelle = models.CharField("Libellé", max_length=120)
    date_debut = models.DateField("Date de début")
    date_fin = models.DateField("Date de fin")
    montant_budget = models.DecimalField(
        "Montant du budget",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    modifie_le = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        db_table = "budgets"  # correspond au SQL
        ordering = ["-date_debut", "-id"]
        verbose_name = "Budget"
        verbose_name_plural = "Budgets"
        indexes = [
            models.Index(fields=["utilisateur"], name="idx_budget_user"),
            models.Index(fields=["date_debut", "date_fin"], name="idx_periode"),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(date_fin__gte=F("date_debut")),
                name="budget_periode_valide",
            ),
            models.CheckConstraint(
                check=Q(montant_budget__gte=0),
                name="budget_montant_positif",
            ),
        ]
        # (optionnel) Empêcher deux budgets avec le même libellé pour un même utilisateur et période exacte
        # unique_together = (("utilisateur", "libelle", "date_debut", "date_fin"),)

    def __str__(self):
        return f"{self.libelle} ({self.date_debut} → {self.date_fin})"

    # ----- Agrégats & états pratiques -----

    @property
    def total_depense(self) -> Decimal:
        total = self.depenses.aggregate(s=Sum("montant"))["s"]
        return total or Decimal("0")

    @property
    def restant(self) -> Decimal:
        return (self.montant_budget or Decimal("0")) - self.total_depense

    @property
    def statut(self) -> str:
        """OK / COMPLET / DEPASSE (comme dans la vue SQL)"""
        if self.total_depense > self.montant_budget:
            return "DEPASSE"
        if self.total_depense == self.montant_budget:
            return "COMPLET"
        return "OK"


class Depense(models.Model):
    # 🔗 Propriétaire de la dépense
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="depenses",
        verbose_name="Utilisateur",
    )

    date_depense = models.DateField("Date de dépense")
    objet = models.CharField("Objet", max_length=255)
    montant = models.DecimalField(
        "Montant",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    budget = models.ForeignKey(
        Budget,
        related_name="depenses",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Budget associé",
    )
    cree_le = models.DateTimeField("Créé le", auto_now_add=True)
    modifie_le = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        db_table = "depenses"  # correspond au SQL
        ordering = ["-date_depense", "-id"]
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"
        indexes = [
            models.Index(fields=["utilisateur"], name="idx_depense_user"),
            models.Index(fields=["date_depense"], name="idx_date"),
            models.Index(fields=["budget"], name="idx_budget"),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(montant__gte=0),
                name="depense_montant_positif",
            ),
        ]

    def __str__(self):
        return f"{self.date_depense} · {self.objet} · {self.montant}"
