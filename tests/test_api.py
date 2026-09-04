"""Integration tests for RevBack FastAPI REST API Endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.db_models import (
    Invoice, Customer, HumanApproval, ApprovalStatus, ApprovalType,
    InvoiceStatus, RecoveryStage
)


@pytest.mark.asyncio
async def test_root_and_health_endpoints(client: AsyncClient):
    """Verifies service discovery and system health checks."""
    root_res = await client.get("/")
    assert root_res.status_code == 200
    root_data = root_res.json()
    assert root_data["status"] == "online"
    assert "/docs" in root_data["docs"]

    health_res = await client.get("/health")
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["status"] == "healthy"
    assert "llm_engine" in health_data


@pytest.mark.asyncio
async def test_seed_database_and_list_invoices(client: AsyncClient):
    """Tests synthetic dataset seeding and invoice query filtering."""
    # 1. Seed database with 15 invoices
    seed_res = await client.post(
        "/api/v1/simulation/seed",
        json={"count": 15, "clear_existing": True, "seed": 42},
    )
    assert seed_res.status_code == 201
    seed_data = seed_res.json()
    assert seed_data["invoices_created"] == 15
    assert seed_data["customers_created"] > 0

    # 2. List all invoices
    list_res = await client.get("/api/v1/invoices")
    assert list_res.status_code == 200
    invoices = list_res.json()
    assert len(invoices) == 15
    assert "risk_score" in invoices[0]
    assert "customer" in invoices[0]

    # 3. Filter by stage
    filter_res = await client.get("/api/v1/invoices?stage=INTAKE")
    assert filter_res.status_code == 200
    assert len(filter_res.json()) > 0


@pytest.mark.asyncio
async def test_invoice_detail_and_evidence_bundle(client: AsyncClient):
    """Tests invoice deep dive and certified evidence bundle generation."""
    # Seed data
    await client.post("/api/v1/simulation/seed", json={"count": 5, "seed": 10})

    invoices = (await client.get("/api/v1/invoices")).json()
    first_id = invoices[0]["id"]

    # 1. Detailed Invoice View
    detail_res = await client.get(f"/api/v1/invoices/{first_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == first_id
    assert "customer" in detail
    assert "promises" in detail
    assert "audit_logs" in detail

    # 2. Evidence Bundle
    bundle_res = await client.get(f"/api/v1/invoices/{first_id}/evidence-bundle")
    assert bundle_res.status_code == 200
    bundle = bundle_res.json()
    assert "evidence_bundle_id" in bundle
    assert "certifying_statement" in bundle
    assert "debtor_profile" in bundle


@pytest.mark.asyncio
async def test_process_invoice_agent_cycle(client: AsyncClient):
    """Tests autonomous execution of a single invoice through LangGraph agent."""
    await client.post("/api/v1/simulation/seed", json={"count": 5, "seed": 20})

    invoices = (await client.get("/api/v1/invoices")).json()
    target_invoice = invoices[0]

    proc_res = await client.post(f"/api/v1/invoices/{target_invoice['id']}/process")
    assert proc_res.status_code == 200
    proc_data = proc_res.json()
    assert proc_data["invoice_id"] == target_invoice["id"]
    assert proc_data["current_stage"] in ("ACT", "DIAGNOSE", "PROMISE_TRACKING")
    assert proc_data["payment_link_url"] is not None
    assert proc_data["dispatched_message"] is not None


@pytest.mark.asyncio
async def test_inbound_message_dispute_and_promise(client: AsyncClient):
    """Tests inbound debtor reply ingestion, intent parsing, and dispute freezing."""
    await client.post("/api/v1/simulation/seed", json={"count": 5, "seed": 30})
    invoices = (await client.get("/api/v1/invoices")).json()
    target_id = invoices[0]["id"]

    # 1. Debtor disputes invoice
    disp_msg = "This invoice is wrong! We never received the second shipment. We dispute this charge."
    inbound_res = await client.post(
        f"/api/v1/invoices/{target_id}/inbound-message",
        json={"message": disp_msg, "channel": "EMAIL"},
    )
    assert inbound_res.status_code == 200
    disp_data = inbound_res.json()
    assert disp_data["intent"] == "DISPUTE"
    assert disp_data["is_disputed"] is True

    # Check that invoice status transitioned to DISPUTED
    detail = (await client.get(f"/api/v1/invoices/{target_id}")).json()
    assert detail["status"] == "DISPUTED"

    # 2. Debtor commits to a promise
    promise_msg = "We will transfer ₹50,000 by this Friday. Please hold off."
    promise_res = await client.post(
        f"/api/v1/invoices/{target_id}/inbound-message",
        json={"message": promise_msg, "channel": "WHATSAPP"},
    )
    assert promise_res.status_code == 200
    p_data = promise_res.json()
    assert p_data["has_promise"] is True
    assert p_data["promised_amount_paise"] == 50_000_00


@pytest.mark.asyncio
async def test_human_approval_resolution(
    client: AsyncClient,
    db_session: AsyncSession,
):
    """Tests supervisor approval resolution queue."""
    # Seed an approval in DB
    await client.post("/api/v1/simulation/seed", json={"count": 5, "seed": 40})
    invoices = (await client.get("/api/v1/invoices")).json()
    first_id = invoices[0]["id"]

    approval = HumanApproval(
        invoice_id=first_id,
        action_type=ApprovalType.LEGAL_NOTICE,
        proposed_action_details={"level": 6, "reason": "3 missed promises"},
        confidence=0.95,
        threshold=0.85,
        status=ApprovalStatus.PENDING,
    )
    db_session.add(approval)
    await db_session.commit()

    # 1. List approvals
    appr_res = await client.get("/api/v1/approvals")
    assert appr_res.status_code == 200
    approvals = appr_res.json()
    assert len(approvals) >= 1

    # 2. Resolve approval
    target_appr_id = approvals[0]["id"]
    resolve_res = await client.post(
        f"/api/v1/approvals/{target_appr_id}/resolve",
        json={
            "decision": "APPROVED",
            "reviewer_id": "counsel@merchant.com",
            "review_notes": "Reviewed ledger and correspondence. Approved for formal notice.",
        },
    )
    assert resolve_res.status_code == 200
    res_data = resolve_res.json()
    assert res_data["status"] == "APPROVED"
    assert "approved" in res_data["next_step"].lower()


@pytest.mark.asyncio
async def test_dashboard_metrics_summary(client: AsyncClient):
    """Tests calculation of executive revenue recovery KPIs."""
    await client.post("/api/v1/simulation/seed", json={"count": 10, "seed": 50})

    metrics_res = await client.get("/api/v1/metrics/summary")
    assert metrics_res.status_code == 200
    data = metrics_res.json()

    assert data["total_invoices_count"] >= 10
    assert data["total_invoiced_inr"] > 0
    assert "stage_breakdown" in data
    assert "estimated_roi_multiple" in data


@pytest.mark.asyncio
async def test_simulation_run_batch_benchmark(client: AsyncClient):
    """Tests head-to-head empirical simulation endpoint."""
    sim_res = await client.post(
        "/api/v1/simulation/run",
        json={"invoice_count": 10, "seed": 42, "include_baseline": True},
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()

    assert "baseline" in sim_data
    assert "agent" in sim_data
    assert "comparative" in sim_data
    assert "uplift_percentage_points" in sim_data["comparative"]
    assert "roi_multiple" in sim_data["comparative"]
    assert sim_data["comparative"]["roi_multiple"] > 1.0
