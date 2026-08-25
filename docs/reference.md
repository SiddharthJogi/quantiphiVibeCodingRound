# Reference: Subscription Tracker & Renewal Dashboard

## 1. Backend Models (Pydantic)
```python
from datetime import date, datetime
from enum import StrEnum
from decimal import Decimal
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class BillingCycle(StrEnum):
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"

class SubscriptionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"

class SubscriptionCreate(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=100)
    cost: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)
    billing_cycle: BillingCycle
    next_renewal_date: date

class SubscriptionUpdate(BaseModel):
    service_name: str | None = None
    cost: Decimal | None = Field(None, gt=Decimal("0.00"), decimal_places=2)
    billing_cycle: BillingCycle | None = None
    next_renewal_date: date | None = None
    status: SubscriptionStatus | None = None

class SubscriptionEntity(SubscriptionCreate):
    id: UUID = Field(default_factory=uuid4)
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Computed (server adds these before sending to frontend)
class ComputedSubscriptionDTO(BaseModel):
    id: UUID
    service_name: str
    cost: float
    billing_cycle: BillingCycle
    next_renewal_date: str
    status: SubscriptionStatus
    normalized_monthly_cost: float
    days_until_renewal: int
    is_renewing_soon: bool
    is_overdue: bool

class DashboardMetricsDTO(BaseModel):
    total_monthly_burn_rate: float
    upcoming_renewals_count: int
    total_subscriptions: int
    active_count: int
    paused_count: int
    monthly_savings_simulation: float
```
Store: `SUBSCRIPTIONS: dict[UUID, SubscriptionEntity] = {}` in-memory, module-level.

## 2. Core Formulas (server-side only)
```python
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
```
`upcoming_renewals_count` = count of ACTIVE subs where `is_renewing_soon` is True.

## 3. API Endpoints
| Method | Route | Body | Returns |
|---|---|---|---|
| GET | `/api/v1/subscriptions` | — | `{subscriptions: ComputedSubscriptionDTO[], metrics: DashboardMetricsDTO}` |
| POST | `/api/v1/subscriptions` | `SubscriptionCreate` | `ComputedSubscriptionDTO` |
| PATCH | `/api/v1/subscriptions/{id}/toggle` | — | `{id, status, metrics}` |
| PUT | `/api/v1/subscriptions/{id}` | `SubscriptionUpdate` | `ComputedSubscriptionDTO` |
| DELETE | `/api/v1/subscriptions/{id}` | — | `{success: true, id}` |
| GET | `/api/v1/subscriptions/metrics` | — | `DashboardMetricsDTO` |

Frontend calls these; never computes cost/date logic itself.

## 4. Frontend Spec
**Entry form fields:** service name (text) · cost (number, `step=0.01`, `min=0.01`) · billing cycle (`<select>`: Monthly/Yearly) · next renewal date (`<input type="date">`) · Submit button.

**Metrics row (2 cards):**
- `MONTHLY CASH-FLOW BURN` — `total_monthly_burn_rate` as currency
- `RENEWALS IN NEXT 7 DAYS` — `upcoming_renewals_count`, amber accent if > 0

**Subscription grid columns:** Service | Cost | Cycle | Monthly Equiv | Next Renewal | Days Left | Status | Action (toggle switch)

**Badge rule:** if `is_renewing_soon` → amber badge "Renewing Soon". If `is_overdue` → red "Overdue" badge instead (never both).

**Toggle (Vibe Check) flow:**
1. On click: optimistically add/remove `.row-paused` class, then `PATCH /toggle`.
2. On response: replace with server's fresh `metrics` (source of truth) and refetch list or update row in place.
3. On failure: revert class, show error.

## 5. CSS Tokens (minimal dark theme)
```css
:root {
  --bg-primary: #0b0f19;
  --bg-surface: rgba(18, 24, 38, 0.9);
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-blue: #3b82f6;
  --caution-amber: #f59e0b;
  --caution-amber-bg: rgba(245, 158, 11, 0.15);
  --danger-red: #ef4444;
  --danger-red-bg: rgba(239, 68, 68, 0.15);
  --radius-md: 10px;
}
.row-paused {
  opacity: 0.45;
  filter: grayscale(80%);
}
.row-paused .service-cost {
  text-decoration: line-through;
  color: var(--text-muted);
}
.badge-renewing-soon {
  background: var(--caution-amber-bg);
  color: var(--caution-amber);
  border-radius: var(--radius-md);
  padding: 2px 8px;
}
.badge-overdue {
  background: var(--danger-red-bg);
  color: var(--danger-red);
  border-radius: var(--radius-md);
  padding: 2px 8px;
}
```

## 6. Edge Cases (must handle)
| Case | Rule |
|---|---|
| `renewal_date < today` | `is_overdue=true`, red badge, NOT "Renewing Soon" |
| `renewal_date == today` (delta=0) | `is_renewing_soon=true`, amber badge |
| Boundary delta = 7 | still `is_renewing_soon=true` |
| Boundary delta = 8 | `is_renewing_soon=false` |
| Yearly float precision (e.g. 99.99/12) | use `Decimal`, round to 2dp — never raw float division |
| Cost ≤ 0 | reject at Pydantic validator (`gt=0`) |
| Date parsing | treat as plain `YYYY-MM-DD` calendar date, no timezone conversion |
| Page reload | acceptable to lose state (in-memory only) — not graded on persistence |