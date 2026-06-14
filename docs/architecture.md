# Architecture

## Reconstruction boundary

This pull request establishes a modular-monolith skeleton without pretending that unfinished prototype behavior is production safe.

```text
Browser -> FastAPI application factory -> Jinja templates
                         |
                         +-> deterministic travel guardrail engine
                         |
                         +-> provider adapters (Amadeus/payment placeholders)
```

The application lifespan loads validated policy configuration once at startup. Route handlers are currently limited to the landing page and operational health checks. Domain workflows are deliberately deferred rather than copied into route handlers from the unsafe prototype.

## Decisions

1. **Preserve before replacing.** Every original tracked artifact is archived under `archive/legacy-upload/` and listed in `docs/reconstruction-map.md`.
2. **Modular monolith.** A single deployable application is the intended core; mock merchants may later run separately to simulate external services.
3. **Consumer marketplace.** The product serves individual, business, and group
   travelers. Business travel is an account type, not the organizing domain.
4. **Deterministic controls first.** Pricing, eligibility, order state, refunds,
   fraud decisions, and payment authorization remain ordinary validated code.
   No LLM is needed to compile, test, or run the application.
5. **Provider boundaries.** Amadeus, Stripe, Datafast, and future providers are
   adapters behind internal contracts; provider payloads never become the
   canonical order or money model.
6. **Simulation disclosure.** The interface and OpenAPI description state that no real booking or payment occurs.
7. **No false security facade.** Identity, persistence, booking, and payment are disabled rather than implemented as unsafe in-memory production substitutes.

## Deferred boundaries

Persistence, trip/order state machines, OAuth 2.0/OIDC identity, RBAC, support
workflows, audit, durable jobs, Amadeus, UCP, payment adapters, webhook
processing, fraud controls, observability, and full accessible workflows are
next-phase work. The complete target and deliberately deferred decisions are in
`docs/consumer-product-requirements.md`.
