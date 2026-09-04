# RevBack — AI Revenue Recovery & Escalation Agent

Autonomous revenue-recovery agent built for Razorpay Buildathon 2026 (Track 3: AI Revenue Recovery).

## Architecture & Overview
- **Agent Core**: LangGraph stateful recovery lifecycle engine.
- **Decision Engine**: Deterministic policy engine with 7 escalation levels + Confidence Gating.
- **LLM Gateway**: LiteLLM router + Instructor structured extraction + smart tone adaptation.
- **Razorpay Integration**: Invoices API, Payment Links API, Customers API, and Webhook verification.
- **Evaluation**: Comparative simulation against standard static dunning baseline measuring Recovery Rate (%), DSO reduction, and Cost-per-Recovery.
