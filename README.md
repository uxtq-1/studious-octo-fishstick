# Consumer Travel Marketplace

A reconstructed, development-only foundation for an AI-assisted **consumer travel
marketplace** for individuals, businesses, and groups. The product direction is
Amadeus-backed travel discovery and booking, provider-neutral payments, and an
optional AI concierge. The recovery phase preserves every flattened source
artifact for later, audited migration.

> **Demonstration limitation:** the current application does not make real reservations, process payments, authenticate users, or provide a production booking workflow. Those capabilities are intentionally deferred until persistence, authorization, audit, and payment controls are implemented.

## What is restored

- A FastAPI application factory with lifespan-loaded deterministic travel guardrails.
- Correct `src/` package layout, Jinja templates, static assets, and mock-merchant package.
- Strict decimal-based evaluation for baseline price, cabin, trip-total, and review checks.
- Operational startup, readiness, and liveness endpoints.
- Compilation, application, policy, formatting, lint, type, and security test configuration.
- A complete archive and migration map for the original flattened upload.

## Requirements

- Python 3.12+

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
uvicorn travel_agent.main:app --reload
```

Open <http://127.0.0.1:8000> or API documentation at <http://127.0.0.1:8000/docs>.

## Tests and checks

```bash
python -m compileall src tests mock_merchants
ruff check .
ruff format --check .
mypy src
pytest --cov=travel_agent --cov-report=term-missing
bandit -r src
pip-audit
```

## Configuration

Copy `.env.example` to `.env`. Environment variables use the `TRAVEL_AGENT_`
prefix. The legacy-compatible travel guardrail example is in
`config/policy.example.yaml` and uses decimal strings to avoid binary
floating-point money calculations.

## Architecture

The target is a modular monolith: HTTP delivery, identity, trips, Amadeus
adapters, provider-neutral payments, orders, notifications, support, audit, and
optional AI planning remain explicit boundaries. Mock providers simulate
external systems. See the [consumer product requirements](docs/consumer-product-requirements.md),
[API contracts](docs/api-contracts.md), [MCP boundary](docs/mcp.md),
[Terraform foundation](infra/terraform/README.md), [architecture](docs/architecture.md),
[Firebase and Flutter integration](docs/firebase-flutter.md), and
[reconstruction map](docs/reconstruction-map.md).

## Flutter client

The initial cross-platform client lives in `clients/flutter_app`. It is a safe
shell with no embedded Firebase project identifiers or provider secrets. See
`docs/firebase-flutter.md` before generating platform-specific Firebase options.

## Mock users

None in this phase. Authentication is intentionally not represented by an insecure placeholder. A clearly marked local identity provider is planned for the identity-and-approvals phase.

## Security reporting

Do not include secrets or personal data in reports. Open a private security advisory in the repository hosting service when available. This project makes no claim of regulatory certification; documentation describes control intentions and known gaps only.

## Deployment guidance

This phase is suitable for local development and CI validation only. Do not expose it as a booking service. Production deployment remains blocked on authentication, authorization, persistent state, CSRF controls, trusted-host configuration, audit storage, SSRF defenses, and reviewed payment integrations.
