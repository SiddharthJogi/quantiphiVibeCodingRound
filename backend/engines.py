from datetime import date
from decimal import Decimal
from models import BillingCycle, SubscriptionEntity, SubscriptionStatus

def calculate_normalized_monthly_cost(cost: Decimal, cycle: BillingCycle) -> Decimal:
    if cycle == BillingCycle.YEARLY:
        return (cost / Decimal("12")).quantize(Decimal("0.01"))
    return cost.quantize(Decimal("0.01"))

def evaluate_renewal_urgency(renewal_date: date, ref: date | None = None) -> tuple[int, bool, bool]:
    ref = ref or date.today()
    delta = (renewal_date - ref).days
    return delta, (0 <= delta <= 7), (delta < 0)

def calculate_burn_metrics(subs: list[SubscriptionEntity]) -> dict:
    burn = savings = Decimal("0.00")
    for s in subs:
        m = calculate_normalized_monthly_cost(s.cost, s.billing_cycle)
        if s.status == SubscriptionStatus.ACTIVE:
            burn += m
        else:
            savings += m
    return {"total_monthly_burn_rate": float(burn), "monthly_savings_simulation": float(savings)}
