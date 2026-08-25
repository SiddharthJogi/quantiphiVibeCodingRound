from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID
from typing import Any
from datetime import datetime, timezone

from models import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionEntity,
    ComputedSubscriptionDTO,
    DashboardMetricsDTO,
    SubscriptionStatus
)
from store import SUBSCRIPTIONS
from engines import calculate_normalized_monthly_cost, evaluate_renewal_urgency, calculate_burn_metrics

app = FastAPI(title="Subscription Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def compute_dto(entity: SubscriptionEntity) -> ComputedSubscriptionDTO:
    norm_cost = calculate_normalized_monthly_cost(entity.cost, entity.billing_cycle)
    delta, renewing_soon, overdue = evaluate_renewal_urgency(entity.next_renewal_date)
    return ComputedSubscriptionDTO(
        id=entity.id,
        service_name=entity.service_name,
        cost=float(entity.cost),
        billing_cycle=entity.billing_cycle,
        next_renewal_date=entity.next_renewal_date.isoformat(),
        status=entity.status,
        normalized_monthly_cost=float(norm_cost),
        days_until_renewal=delta,
        is_renewing_soon=renewing_soon,
        is_overdue=overdue
    )

def get_dashboard_metrics() -> DashboardMetricsDTO:
    subs = list(SUBSCRIPTIONS.values())
    burn_metrics = calculate_burn_metrics(subs)
    
    upcoming_count = sum(1 for s in subs if s.status == SubscriptionStatus.ACTIVE and evaluate_renewal_urgency(s.next_renewal_date)[1])
    active_count = sum(1 for s in subs if s.status == SubscriptionStatus.ACTIVE)
    paused_count = sum(1 for s in subs if s.status == SubscriptionStatus.PAUSED)
    
    return DashboardMetricsDTO(
        total_monthly_burn_rate=burn_metrics["total_monthly_burn_rate"],
        upcoming_renewals_count=upcoming_count,
        total_subscriptions=len(subs),
        active_count=active_count,
        paused_count=paused_count,
        monthly_savings_simulation=burn_metrics["monthly_savings_simulation"]
    )

@app.get("/api/v1/subscriptions")
async def get_subscriptions() -> dict[str, Any]:
    dtos = [compute_dto(sub) for sub in SUBSCRIPTIONS.values()]
    metrics = get_dashboard_metrics()
    return {"subscriptions": dtos, "metrics": metrics.model_dump()}

@app.post("/api/v1/subscriptions", response_model=ComputedSubscriptionDTO)
async def create_subscription(sub: SubscriptionCreate):
    entity = SubscriptionEntity(**sub.model_dump())
    SUBSCRIPTIONS[entity.id] = entity
    return compute_dto(entity)

@app.patch("/api/v1/subscriptions/{id}/toggle")
async def toggle_subscription(id: UUID) -> dict[str, Any]:
    if id not in SUBSCRIPTIONS:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    entity = SUBSCRIPTIONS[id]
    entity.status = SubscriptionStatus.PAUSED if entity.status == SubscriptionStatus.ACTIVE else SubscriptionStatus.ACTIVE
    entity.updated_at = datetime.now(timezone.utc)
    
    metrics = get_dashboard_metrics()
    return {"id": str(id), "status": entity.status, "metrics": metrics.model_dump()}

@app.put("/api/v1/subscriptions/{id}", response_model=ComputedSubscriptionDTO)
async def update_subscription(id: UUID, sub: SubscriptionUpdate):
    if id not in SUBSCRIPTIONS:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    entity = SUBSCRIPTIONS[id]
    update_data = sub.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(entity, key, value)
    entity.updated_at = datetime.now(timezone.utc)
    
    return compute_dto(entity)

@app.delete("/api/v1/subscriptions/{id}")
async def delete_subscription(id: UUID) -> dict[str, Any]:
    if id not in SUBSCRIPTIONS:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    del SUBSCRIPTIONS[id]
    return {"success": True, "id": str(id)}

@app.get("/api/v1/subscriptions/metrics", response_model=DashboardMetricsDTO)
async def get_metrics():
    return get_dashboard_metrics()

from pathlib import Path
from fastapi.staticfiles import StaticFiles

frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

