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
