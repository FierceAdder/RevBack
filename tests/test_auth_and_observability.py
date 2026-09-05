"""Tests for Auth, Multi-Tenancy, Team Management, and Observability."""

import pytest
from httpx import AsyncClient
from src.evaluation.cost_tracker import CostTracker


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    # 1. Register a new tenant & admin user
    reg_payload = {
        "company_name": "Test Acme Corp",
        "full_name": "Alice Smith",
        "email": "alice@acme.com",
        "password": "SecurePassword123!",
    }
    res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "alice@acme.com"
    assert data["user"]["role"] == "ADMIN"
    assert data["user"]["tenant"]["name"] == "Test Acme Corp"

    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get current profile /me
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "alice@acme.com"

    # 3. Login with credentials
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@acme.com", "password": "SecurePassword123!"},
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


@pytest.mark.asyncio
async def test_api_key_lifecycle(client: AsyncClient):
    # Register user first
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "company_name": "Fintech Global",
            "full_name": "Bob Vance",
            "email": "bob@vance.com",
            "password": "Password789!",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create an API key
    key_res = await client.post(
        "/api/v1/auth/api-keys",
        headers=headers,
        json={"name": "ERP Auto Sync", "scope": "WRITE"},
    )
    assert key_res.status_code == 201
    key_data = key_res.json()
    assert key_data["name"] == "ERP Auto Sync"
    assert key_data["scope"] == "WRITE"
    assert "raw_key" in key_data
    assert key_data["raw_key"].startswith("rzb_live_")
    key_id = key_data["id"]

    # 2. List API keys
    list_res = await client.get("/api/v1/auth/api-keys", headers=headers)
    assert list_res.status_code == 200
    keys = list_res.json()
    assert any(k["id"] == key_id for k in keys)

    # 3. Revoke API key
    del_res = await client.delete(f"/api/v1/auth/api-keys/{key_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "revoked"

    # Verify key is no longer in active list
    list_after = await client.get("/api/v1/auth/api-keys", headers=headers)
    assert not any(k["id"] == key_id for k in list_after.json())


@pytest.mark.asyncio
async def test_team_members_management(client: AsyncClient):
    reg = await client.post(
        "/api/v1/auth/register",
        json={
            "company_name": "Trident Infra",
            "full_name": "Charlie Admin",
            "email": "charlie@trident.com",
            "password": "Password123!",
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List initial team (should include admin)
    team_res = await client.get("/api/v1/auth/team", headers=headers)
    assert team_res.status_code == 200
    team = team_res.json()
    assert len(team) >= 1
    assert team[0]["email"] == "charlie@trident.com"

    # 2. Invite a new Supervisor
    invite_res = await client.post(
        "/api/v1/auth/team",
        headers=headers,
        json={
            "full_name": "David Supervisor",
            "email": "david@trident.com",
            "role": "SUPERVISOR",
        },
    )
    assert invite_res.status_code == 201
    invited = invite_res.json()
    assert invited["email"] == "david@trident.com"
    assert invited["role"] == "SUPERVISOR"

    # 3. List team again and verify count
    team_after = await client.get("/api/v1/auth/team", headers=headers)
    assert len(team_after.json()) >= 2


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(client: AsyncClient):
    res = await client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers.get("content-type", "")
    content = res.text
    assert "revback_invoices_processed_total" in content
    assert "revback_revenue_recovered_paise_total" in content
    assert "revback_agent_run_duration_seconds" in content


def test_cost_tracker_usage_and_roi():
    cost = CostTracker.record_usage("gemini-2.0-flash", prompt_tokens=10_000, completion_tokens=2_000)
    assert cost > 0

    summary = CostTracker.get_token_summary()
    assert summary["total_tokens"] >= 12_000
    assert summary["total_cost_usd"] > 0

    roi = CostTracker.calculate_roi(recovered_paise=5_000_000, total_token_cost_usd=summary["total_cost_usd"])
    assert roi["recovered_inr"] == 50_000.0
    assert roi["roi_multiple"] > 100
