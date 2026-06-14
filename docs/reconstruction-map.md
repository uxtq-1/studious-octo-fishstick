# Flattened repository reconstruction map

## Preservation rule

The original upload is preserved byte-for-byte through Git renames in `archive/legacy-upload/`. The archive is provenance, not importable application code. Empty and duplicate-numbered files are retained because their absence of content is itself part of the source inventory.

## Migration map

| Original artifact(s) | Observed content | Restored or planned destination |
|---|---|---|
| `__init__ (14).py` | FastAPI factory and lifespan code | Concepts restored in `src/travel_agent/main.py`; original archived |
| `__init__.py` | YAML application configuration | Example settings restored under `config/`; original archived |
| `pyproject.toml` | HTML base template | Valid project metadata restored at root; template rebuilt under `src/travel_agent/templates/` |
| `README.md` | Trip booking Jinja template with unsafe DOM rendering | Archived as UI reference; real README restored; workflow UI deferred |
| `CLAUDE.md`, `download`, `skills.md` | Approval/trip Jinja templates | Archived; future destinations under `templates/approvals/` and `templates/trips/` |
| `base.html`, `approvals.html`, `index.html`, `inventory.json` | Python models/services/merchant server in wrong file types | Archived; selected safe concepts reconstructed in typed modules; remaining behavior deferred |
| `settings.yaml` | Company travel policy | Normalized example policy restored at `config/policy.example.yaml` |
| `routes (18).py`, `test_ap2_mandates.py` | FastAPI application routes | Archived; unsafe in-memory/background-task routes deferred |
| `conftest.py`, `test_mock_merchants.py` | Runtime merchant/order code rather than tests | Archived; replaced with actual tests under `tests/` |
| `flight_merchant.py`, `client.py`, `merchants.py`, `prompts.py`, `routes.py`, `approval_detail.html`, numbered empty `__init__` files | Empty placeholders | Archived; package placeholders created only where needed |
| `__init__ (1).py` | JSON merchant inventory | Archived; a valid empty JSON schema restored at `mock_merchants/inventory.json`; data migration deferred |
| `__init__ (2).py`, `transport_merchant.py`, `hotel_merchant.py` | Mock merchant servers with swapped/misleading names | Archived; clean merchant module boundaries restored under `mock_merchants/` |
| `__init__ (5).py`, `models*.py`, `orders.py`, `loader.py`, `engine (10).py` | UCP/AP2/domain/database/config models | Archived; policy model subset restored; remaining modules deferred pending behavior tests |
| `engine.py`, `handler.py`, `mandates.py`, `payment.py`, `signing.py` | Policy, orchestrator, AP2, prompts/signing concepts | Archived; deterministic policy restored; AI/payment/security work deferred |
| `cli.py`, `discovery.py`, `search.py` | AP2/UCP/search services | Archived; future adapter/service destinations documented in master plan |

## Accounting

All 50 tracked source artifacts present at reconstruction start were moved to the archive. No original artifact was deleted. New files are clean replacements and do not mutate archived provenance.
