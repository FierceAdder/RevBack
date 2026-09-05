# RevBack — Autonomous AI Revenue Recovery & Escalation Agent

> **Razorpay Buildathon 2026 — Track 3: AI Revenue Recovery & Escalation Agent**  
> An autonomous, relationship-preserving B2B receivables recovery system powered by LangGraph, deterministic policy gating, LiteLLM, and the Razorpay financial suite.

[![Tests](https://img.shields.io/badge/tests-54%20passed-success)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.12-blue)](https://python.org)
[![Next.js](https://img.shields.io/badge/next.js-16.3-black)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115-teal)](https://fastapi.tiangolo.com)
[![Razorpay](https://img.shields.io/badge/razorpay-v1.4-blue)](https://razorpay.com)

---

## 🚀 Executive Summary

Traditional accounts receivable (AR) processes suffer from two extremes: either generic, aggressive dunning emails that burn enterprise customer relationships, or manual spreadsheets that let millions in overdue invoices slip through the cracks.

**RevBack** replaces manual AR chasing with an autonomous, high-EQ agent that:
1. **Understands the Debtor**: Dynamically tailors communication tone based on customer tier (Strategic Enterprise, Growth, Standard) and days overdue.
2. **Predicts Recovery Likelihood**: Employs logistic recovery probability modeling $P(\text{recovery})$ incorporating invoice size, payment velocity, and broken promise penalties.
3. **Offers Flexible Solutions**: Automatically negotiates structured installment payment plans and generates live Razorpay Payment Links with individual expiration dates.
4. **Protects Brand Reputation**: Implements deterministic policy guardrails (Levels 0–6) and **human-in-the-loop approval gating** with true LangGraph Redis thread checkpointing.
5. **Reconciles in Real Time**: Validates incoming Razorpay webhooks via HMAC-SHA256 signatures to instantly settle invoices, resolve active promises, and halt dunning.

---

## 🏛️ System Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │               Web Dashboard                  │
                    │   Next.js 16 · TailwindCSS · Framer Motion   │
                    │  (Overview, Ledger, Approvals, Audit, Admin) │
                    └───────────────────────▲──────────────────────┘
                                            │ REST / WebSocket
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             FastAPI API Gateway                                  │
│  - JWT Bearer & API Key Auth (`rzb_live_...`)  - Rate Limiting (SlowAPI 120/min) │
│  - Multi-Tenant Isolation (Tenant UUID)        - Prometheus `/metrics` Export    │
└───────────────▲───────────────────────────▲──────────────────────────▲───────────┘
                │                           │                          │
                ▼                           ▼                          ▼
┌──────────────────────────────┐  ┌──────────────────┐  ┌──────────────────────────┐
│   LangGraph Recovery Core    │  │ Deterministic    │  │    Razorpay Gateway      │
│ - Redis State Checkpointing  │  │ Policy Engine    │  │ - Payment Links (SMS/EML)│
│ - Pause at Human Gate        │  │ - Levels 0 to 6  │  │ - Webhook HMAC-SHA256    │
│ - Resume on Approval         │  │ - Dispute Halts  │  │ - Invoices & Customers   │
└───────────────▲──────────────┘  └──────────────────┘  └──────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         Background Workers & Infrastructure                      │
│  - Celery Worker (4 concurrency)       - Celery Beat (Periodic cron schedules)   │
│  - Redis 7 (Checkpoints & Broker)      - PostgreSQL 16 (Bitemporal Audit Ledger) │
│  - Observability (Langfuse Traces)     - Dispatchers (Email, SMS, WhatsApp)      │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quickstart & Running Locally

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** and `npm`
- **Docker & Docker Compose** (Optional, for full containerized stack)

---

### Option A: One-Command Local Development (Recommended)

To start both the FastAPI backend and Next.js frontend with unified logging:

```bash
# 1. Setup virtualenv and install dependencies
npm run setup

# 2. Start fullstack dev server (FastAPI on :8000 + Next.js on :3000/3001)
npm run dev
```

*Press `Ctrl+C` to gracefully terminate both frontend and backend processes.*

---

### Option B: Running Services Individually

If you prefer separate terminal windows:

#### Terminal 1: Backend (FastAPI)
```bash
source .venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Prometheus Metrics: `http://localhost:8000/metrics`

#### Terminal 2: Frontend (Next.js Dashboard)
```bash
npm run dev:frontend
```
- Web Dashboard: `http://localhost:3000` (or `http://localhost:3001` if 3000 is occupied)

#### Terminal 3: Celery Background Worker & Beat (Optional for background cron)
```bash
# Start Celery Worker
npm run dev:worker

# Start Celery Beat Scheduler (hourly promise audits & daily metrics)
npm run dev:beat
```

---

### Option C: Docker Compose

```bash
# Local development with Redis and PostgreSQL
docker compose up --build

# Production stack with Nginx SSL proxy and resource bounds
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 🧪 Testing & Validation

RevBack includes an exhaustive automated test suite covering all policy decisions, risk computations, agent workflows, Razorpay webhooks, and multi-tenant security:

```bash
# Run pytest test suite
npm run test

# Or directly with pytest
source .venv/bin/activate
pytest -v
```

**Test Coverage Summary:**
- `test_agent_graph.py`: LangGraph state transitions, Redis checkpoint pausing & resumption on supervisor approval.
- `test_policy_engine.py`: Deterministic escalation ladder (Intervention Levels 0 through 6).
- `test_confidence_gate.py`: Dynamic confidence scaling with invoice amount.
- `test_risk_scorer.py`: Multi-factor risk calculations (overdue decay, promise penalties, relationship modifiers).
- `test_webhooks.py`: Razorpay HMAC-SHA256 signature verification & idempotent reconciliation.
- `test_auth_and_observability.py`: JWT token lifecycle, API key hashing (`rzb_live_...`), team invitations, and Prometheus counters.
- **54 passing tests in ~20s.**

---

## 🎯 7 Core Track 3 Innovations

### 1. Relationship-Aware Tone & Intervention Ladder
- Deterministic 7-stage policy ladder:
  - **Level 0 (Courtesy Reminder)**: Friendly, helpful check-in.
  - **Level 1 (Standard Reminder)**: Professional notification with payment link.
  - **Level 2 (Urgent Follow-up)**: Firm request citing finance policies.
  - **Level 3 (Account Pause Notice)**: Warning of service/account suspension.
  - **Level 4 (Executive Escalation)**: Formal notice copied to customer VP/CFO.
  - **Level 5 (Pre-Legal Notice)**: Formal demand with statutory 7-day cure period.
  - **Level 6 (Legal Action)**: Automated compilation of bitemporal evidence bundle and referral to legal counsel.
- Tones are mathematically mapped against customer relationship tiers (`STRATEGIC_ACCOUNT`, `GROWTH_PARTNER`, `STANDARD_COMMERCIAL`).

### 2. Logistic Recovery Probability Engine
Computes real-time probability of recovery $P(\text{recovery})$:
$$P(\text{recovery}) = \frac{1}{1 + e^{-z}}$$
Where $z$ integrates:
- Overdue exponential decay ($\lambda = 0.025/\text{day}$)
- Invoice amount penalty for high-ticket exposures
- Broken promise penalties ($-0.85$ per missed promise)
- Relationship tier trust bonuses ($+0.75$ for strategic clients)

### 3. Dynamic Payment Plans & Razorpay Links
When a debtor communicates cash flow difficulties (`REQUEST_EXTENSION`), RevBack:
- Automatically synthesizes a 2–4 installment recovery plan based on customer credit tier.
- Creates individual Razorpay Payment Links for each installment with specific `expire_by` deadlines.
- Automatically transitions the invoice to `PROMISE_TRACKING`.

### 4. Multi-Channel Escalation Cascade
Cascades outreach through optimal channels:
- Email (Resend API / SMTP)
- SMS (Razorpay native notification `notify.sms=true`)
- WhatsApp Business API notifications

### 5. Optimal Send-Time Predictor & Celery Beat
- Analyzes debtor historical response latency and optimal business opening hours (10:00–11:30 AM IST).
- Dispatches outreach via Celery `eta` tasks to maximize read and conversion rates.

### 6. Observability, Tracing & Cost Accounting
- **Langfuse Tracing**: Full prompt and completion traces linked to each invoice ID.
- **Prometheus `/metrics`**: Exports recovery rates, request latencies, and LLM token usage counters.
- **Cost Tracker**: Calculates exact token cost in USD and computes the recovery ROI multiple.

### 7. True LangGraph Redis Checkpointing & Human Gating
- If the agent's confidence falls below the dynamic threshold or reaches high-risk actions (Legal Notice, Debt Forgiveness), the graph **persists state to Redis** and pauses.
- A supervisor can review the draft in the `/approvals` UI.
- Once approved, the graph resumes directly from its checkpointed state without re-running prior nodes.

---

## 📁 Repository Structure

```
RevBack/
├── alembic/                  # Async SQLAlchemy DB migrations
├── docker-compose.yml        # Development Docker stack
├── docker-compose.prod.yml   # Hardened production stack
├── nginx/                    # Nginx reverse proxy configuration
├── pyproject.toml            # Backend dependencies & metadata
├── package.json              # Root script runner
├── scripts/
│   ├── dev.sh                # Unified local launcher
│   └── setup.sh              # One-touch bootstrap
├── src/
│   ├── main.py               # FastAPI application entrypoint
│   ├── config.py             # App configuration & environment validation
│   ├── agent/                # LangGraph stateful recovery agent
│   │   ├── graph.py          # StateGraph definition & human interrupts
│   │   ├── checkpointer.py   # AsyncRedisCheckpointer integration
│   │   ├── payment_plans.py  # Installment generator & Razorpay link creator
│   │   └── tools.py          # Evidence bundler & Razorpay tools
│   ├── api/                  # FastAPI REST endpoints
│   │   ├── routes/           # Invoices, Approvals, Metrics, Auth, Simulation
│   │   └── webhooks.py       # Razorpay HMAC webhook handler
│   ├── auth/                 # Multi-tenancy, JWT auth, and API key management
│   ├── channels/             # Dispatchers (Email, SMS, WhatsApp)
│   ├── db/                   # Database session & init
│   ├── engine/               # Deterministic policy & risk calculation engine
│   ├── llm/                  # LiteLLM client, structured extractors & tone
│   ├── models/               # SQLAlchemy models & Pydantic schemas
│   ├── observability/        # Langfuse tracing & Prometheus metrics
│   ├── razorpay/             # Razorpay API client & webhook signature validator
│   ├── simulation/           # Synthetic dataset & comparative benchmark
│   └── workers/              # Celery background tasks & Beat cron schedules
├── frontend/                 # Next.js 16 Web Dashboard
│   ├── src/
│   │   ├── app/              # App router pages (Overview, Invoices, Approvals, Audit, Settings)
│   │   ├── components/       # Bento UI cards, charts, navigation, modals
│   │   ├── context/          # Auth & Tenant context
│   │   └── lib/              # API client & TypeScript interfaces
└── tests/                    # Pytest test suite (54 test cases)
```

---

## 🔒 Security & Compliance

- **Zero Wildcard CORS**: Restricts origins strictly to configured frontend hosts.
- **Rate Limiting**: Built-in `slowapi` rate limiter (120 req/min general, 20 req/min auth).
- **HMAC Webhook Verification**: Constant-time comparison of `X-Razorpay-Signature` against raw webhook bodies.
- **Tenant Isolation**: All queries enforce tenant foreign keys (`tenant_id`).
- **Cryptographic API Keys**: Generated with high entropy and stored exclusively as SHA-256 hashes.

---

## 📄 License

Built for the **Razorpay Buildathon 2026** by Ashmit. All rights reserved.
