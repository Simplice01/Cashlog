# depenses/views_chat.py
from datetime import date, datetime
from decimal import Decimal
from django.views import View
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from .models import Depense, Budget

DATE_FMT = "%Y-%m-%d"

def _parse_dates(txt: str):
    """
    Retourne (start, end, exact) en dates si trouvé.
    - "aujourd'hui"
    - "ce mois" / "mois en cours"
    - "entre 2025-10-01 et 2025-10-15"
    - "le 2025-10-12" / "2025-10-12"
    """
    t = txt.lower().strip()

    # aujourd'hui
    if "aujourd" in t:
        d = date.today()
        return (None, None, d)

    # mois courant
    if "ce mois" in t or "mois en cours" in t or "mois courant" in t:
        today = date.today()
        start = today.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1)
        else:
            end = start.replace(month=start.month + 1, day=1)
        return (start, end, None)

    # entre AAAA-MM-JJ et AAAA-MM-JJ
    if "entre" in t and "et" in t:
        try:
            part = t.split("entre", 1)[1].strip()
            left, right = [p.strip() for p in part.split("et", 1)]
            start = datetime.strptime(left[:10], DATE_FMT).date()
            end_i = datetime.strptime(right[:10], DATE_FMT).date()
            # borne supérieure exclusive (style Django range)
            end = end_i.replace(day=end_i.day)  # même jour, on traitera <=
            return (start, end, None)
        except Exception:
            pass

    # le AAAA-MM-JJ  OU AAAA-MM-JJ
    for key in ("le ", ""):
        if key in t:
            try:
                idx = t.find(key)
                cand = t[idx + len(key): idx + len(key) + 10]
                exact = datetime.strptime(cand, DATE_FMT).date()
                return (None, None, exact)
            except Exception:
                continue

    return (None, None, None)

def _money(v):
    return f"{Decimal(v or 0):,.2f}".replace(",", " ").replace(".", ",")

def _advice(total: Decimal, budget: Budget | None):
    """Génère un petit conseil en fonction du budget."""
    if not budget:
        if total == 0:
            return "Aucun budget associé et aucune dépense : parfait pour démarrer proprement."
        return "Aucun budget associé : pense à créer/associer un budget pour mieux suivre le restant."
    restant = (budget.montant_budget or Decimal("0")) - (total or Decimal("0"))
    if restant < 0:
        return "Tu as dépassé le budget 🚨 : réduis les dépenses non essentielles et revois l’enveloppe."
    if restant == 0:
        return "Budget atteint au centime près ✅. Évite toute dépense supplémentaire pour ce budget."
    ratio = (total / budget.montant_budget) if budget.montant_budget else Decimal("0")
    if ratio < Decimal("0.5"):
        return "Tu es en dessous de 50% : bon rythme, continue à prioriser l’essentiel."
    if ratio < Decimal("0.8"):
        return "Attention, tu t’approches des 80% : surveille les petits achats impulsifs."
    return "Tu es au-delà de 80% du budget : ralentis et planifie les prochaines dépenses."

class AssistantView(LoginRequiredMixin, View):
    template_name = "depenses/chat.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name)

    def post(self, request: HttpRequest) -> JsonResponse:
        """Attendu: JSON {message: "..."} ; Répond: {reply: "...", items?: [...] }"""
        import json
        payload = json.loads(request.body.decode("utf-8") or "{}")
        msg: str = (payload.get("message") or "").strip()
        if not msg:
            return JsonResponse({"reply": "Dis-moi ce que tu veux savoir (ex: total aujourd’hui, ce mois, entre deux dates, restant du budget…)."})

        start, end, exact = _parse_dates(msg)

        qs = Depense.objects.filter(utilisateur=request.user)
        # Filtrage temporel
        if exact:
            qs = qs.filter(date_depense=exact)
        elif start and end:
            # end inclusif
            qs = qs.filter(date_depense__gte=start, date_depense__lte=end)
        elif "mois" in msg.lower():
            # déjà géré dans _parse_dates, sinon fallback
            pass

        # Filtre budget si l’utilisateur le mentionne : ex. "budget rentrée"
        budget = None
        if "budget" in msg.lower():
            # Cherche un nom de budget approximatif entre guillemets : budget "rentrée"
            import re
            m = re.search(r'budget\s+"([^"]+)"', msg, flags=re.I)
            if not m:
                m = re.search(r"budget\s+'([^']+)'", msg, flags=re.I)
            if m:
                lib = m.group(1)
                budget = (Budget.objects
                          .filter(utilisateur=request.user, libelle__icontains=lib)
                          .order_by("-date_debut")
                          .first())
                if budget:
                    qs = qs.filter(Q(budget=budget) | Q(budget__isnull=True))
            else:
                # S’il dit juste "budget", on prend le plus récent actif couvrant aujourd’hui
                today = date.today()
                budget = (Budget.objects
                          .filter(utilisateur=request.user, date_debut__lte=today, date_fin__gte=today)
                          .order_by("-date_debut")
                          .first())

        # Intent simple
        low = msg.lower()
        wants_list = any(k in low for k in ["liste", "affiche", "détail", "details", "détails", "quels", "montre"])
        wants_total = any(k in low for k in ["total", "combien", "dépensé", "dépense totale", "somme"])
        wants_restant = any(k in low for k in ["reste", "restant", "budget restant", "encore combien"])

        # Calculs
        total = qs.aggregate(s=Sum("montant"))["s"] or Decimal("0")
        items = []
        if wants_list:
            items = list(qs.order_by("-date_depense", "-id").values("date_depense", "objet", "montant")[:50])

        # Formulation période lisible
        if exact:
            periode = f"le {exact.strftime('%Y-%m-%d')}"
        elif start and end:
            periode = f"du {start.strftime('%Y-%m-%d')} au {end.strftime('%Y-%m-%d')}"
        else:
            periode = "la période demandée" if ("entre" in low or "mois" in low) else "toutes les dépenses"

        parts = []
        if wants_total or not (wants_list or wants_restant):
            parts.append(f"Total dépensé sur {periode} : **{_money(total)}** FCFA.")

        if wants_restant:
            if not budget:
                parts.append("Je n’ai pas identifié de budget précis. Donne-moi un nom, par ex. `budget \"rentrée\"`.")
            else:
                dep_budget = Depense.objects.filter(utilisateur=request.user, budget=budget)
                if exact:
                    dep_budget = dep_budget.filter(date_depense=exact)
                elif start and end:
                    dep_budget = dep_budget.filter(date_depense__gte=start, date_depense__lte=end)
                dep_total = dep_budget.aggregate(s=Sum("montant"))["s"] or Decimal("0")
                restant = (budget.montant_budget or Decimal("0")) - dep_total
                parts.append(
                    f"Budget **{budget.libelle}** ({budget.date_debut} → {budget.date_fin}) — "
                    f"dépensé: **{_money(dep_total)}** FCFA, restant: **{_money(restant)}** FCFA."
                )
                parts.append(_advice(dep_total, budget))

        if wants_list:
            if items:
                parts.append(f"Voici jusqu’à 50 lignes pour {periode} (du plus récent au plus ancien).")
            else:
                parts.append(f"Aucune dépense trouvée pour {periode}.")

        reply = "\n".join(parts) if parts else "Que veux-tu savoir ? Exemple : « total aujourd’hui », « liste entre 2025-10-01 et 2025-10-15 », « budget restant », « budget \"rentrée\" »."
        return JsonResponse({"reply": reply, "items": items})
