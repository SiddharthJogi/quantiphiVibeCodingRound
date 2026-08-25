from fastapi.testclient import TestClient
from datetime import date, timedelta
from decimal import Decimal
import pytest

from main import app
from store import SUBSCRIPTIONS

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store():
    # Clear the in-memory store before each test
    SUBSCRIPTIONS.clear()
    yield

def test_create_and_get_subscriptions():
    today = date.today()
    
    # Create valid sub
    res = client.post("/api/v1/subscriptions", json={
        "service_name": "Netflix",
        "cost": 15.99,
        "billing_cycle": "MONTHLY",
        "next_renewal_date": today.isoformat()
    })
    assert res.status_code == 200
    data = res.json()
    assert data["service_name"] == "Netflix"
    assert data["is_renewing_soon"] == True
    assert data["is_overdue"] == False

def test_cost_validation_rejects_zero():
    today = date.today()
    res = client.post("/api/v1/subscriptions", json={
        "service_name": "Free Tier",
        "cost": 0.00,
        "billing_cycle": "MONTHLY",
        "next_renewal_date": today.isoformat()
    })
    assert res.status_code == 422 # Pydantic validation error

def test_yearly_cost_normalization():
    today = date.today()
    res = client.post("/api/v1/subscriptions", json={
        "service_name": "AWS",
        "cost": 99.99,
        "billing_cycle": "YEARLY",
        "next_renewal_date": today.isoformat()
    })
    assert res.status_code == 200
    data = res.json()
    # 99.99 / 12 = 8.3325 -> rounds to 8.33
    assert data["normalized_monthly_cost"] == 8.33

def test_edge_cases_renewal_urgency():
    today = date.today()
    
    # Case 1: Overdue (yesterday)
    yesterday = today - timedelta(days=1)
    res_overdue = client.post("/api/v1/subscriptions", json={
        "service_name": "Overdue Sub",
        "cost": 10.0,
        "billing_cycle": "MONTHLY",
        "next_renewal_date": yesterday.isoformat()
    })
    data = res_overdue.json()
    assert data["is_overdue"] == True
    assert data["is_renewing_soon"] == False

    # Case 2: Boundary delta = 7 (renewing soon)
    in_7_days = today + timedelta(days=7)
    res_7 = client.post("/api/v1/subscriptions", json={
        "service_name": "In 7 Days",
        "cost": 10.0,
        "billing_cycle": "MONTHLY",
        "next_renewal_date": in_7_days.isoformat()
    })
    data = res_7.json()
    assert data["is_overdue"] == False
    assert data["is_renewing_soon"] == True

    # Case 3: Boundary delta = 8 (not renewing soon)
    in_8_days = today + timedelta(days=8)
    res_8 = client.post("/api/v1/subscriptions", json={
        "service_name": "In 8 Days",
        "cost": 10.0,
        "billing_cycle": "MONTHLY",
        "next_renewal_date": in_8_days.isoformat()
    })
    data = res_8.json()
    assert data["is_overdue"] == False
    assert data["is_renewing_soon"] == False

def test_toggle_subscription():
    today = date.today()
    res = client.post("/api/v1/subscriptions", json={
        "service_name": "Netflix",
        "cost": 100.0,
        "billing_cycle": "MONTHLY",
        "next_renewal_date": today.isoformat()
    })
    sub_id = res.json()["id"]

    # Check metrics before toggle
    metrics_res = client.get("/api/v1/subscriptions/metrics")
    assert metrics_res.json()["total_monthly_burn_rate"] == 100.0
    assert metrics_res.json()["monthly_savings_simulation"] == 0.0

    # Toggle to PAUSED
    toggle_res = client.patch(f"/api/v1/subscriptions/{sub_id}/toggle")
    assert toggle_res.status_code == 200
    assert toggle_res.json()["status"] == "PAUSED"
    
    # Check metrics after toggle
    metrics_res = client.get("/api/v1/subscriptions/metrics")
    assert metrics_res.json()["total_monthly_burn_rate"] == 0.0
    assert metrics_res.json()["monthly_savings_simulation"] == 100.0
