# API contracts

The REST API is the canonical automation boundary. HTML routes may call the same
application services, but neither UI templates nor provider payloads define the
domain contract.

## Common protocol

- Base path: `/api/v1`.
- Authentication: OAuth 2.0 access tokens with purpose-specific audiences and
  scopes; browser sessions use secure, HttpOnly, SameSite cookies plus CSRF.
- Errors: `application/problem+json` using RFC 9457 fields plus a safe error code,
  request ID, correlation ID, and field violations.
- Mutations: `Idempotency-Key` is required. The server stores request hashes and
  rejects reuse with a different payload.
- Concurrency: use entity versions/ETags and `If-Match` for selection, checkout,
  support decisions, cancellation, and administrative changes.
- Pagination: opaque cursor, bounded page size, deterministic order.
- Times and money: UTC RFC 3339 event timestamps; local travel date/time plus IANA
  zone; integer minor units plus ISO 4217 currency.
- Responses never include access tokens, provider secrets, payment credentials,
  internal fraud features, or unrestricted personal data.

## Customer and trip resources

```text
POST   /auth/registrations
POST   /auth/sessions
DELETE /auth/sessions/current
GET    /me
PATCH  /me
GET    /me/sessions
DELETE /me/sessions/{session_id}

POST   /travelers
GET    /travelers
GET    /travelers/{traveler_id}
PATCH  /travelers/{traveler_id}
DELETE /travelers/{traveler_id}

POST   /trips
GET    /trips
GET    /trips/{trip_id}
PATCH  /trips/{trip_id}
POST   /trips/{trip_id}/searches
GET    /trips/{trip_id}/searches/{search_id}
GET    /trips/{trip_id}/offers
POST   /trips/{trip_id}/selections
GET    /trips/{trip_id}/itinerary
GET    /trips/{trip_id}/events
POST   /trips/{trip_id}/cancellations
```

Search is asynchronous when provider latency exceeds the request budget. Offers
carry source, retrieval time, expiration, price-verification status, terms,
baggage, accessibility evidence, taxes, fees, and ranking explanations.

## Groups and business accounts

```text
POST   /groups
GET    /groups/{group_id}
POST   /groups/{group_id}/invitations
POST   /groups/{group_id}/participants
PATCH  /groups/{group_id}/participants/{participant_id}
PUT    /groups/{group_id}/guide

POST   /organizations
GET    /organizations/{organization_id}
POST   /organizations/{organization_id}/members
PATCH  /organizations/{organization_id}/members/{member_id}
GET    /organizations/{organization_id}/receipts
```

Invitation acceptance, organizer authority, guide visibility, delegate access,
and organization membership are server-derived relationships—not client roles.

## Cart, orders, payments, and refunds

```text
POST   /carts
GET    /carts/{cart_id}
POST   /carts/{cart_id}/items
DELETE /carts/{cart_id}/items/{item_id}
POST   /carts/{cart_id}/price-verifications
POST   /carts/{cart_id}/checkouts

GET    /orders/{order_id}
GET    /orders/{order_id}/ledger
POST   /orders/{order_id}/confirmations
POST   /orders/{order_id}/cancellations
POST   /orders/{order_id}/refunds

POST   /payment-sessions
GET    /payments/{payment_id}
GET    /refunds/{refund_id}
```

Checkout creates a server-priced snapshot. Payment requests reference that
snapshot; clients cannot submit trusted totals, taxes, fees, settlement state,
or provider confirmation.

## Notifications and support

```text
GET    /notifications
PATCH  /notifications/{notification_id}
GET    /notification-preferences
PUT    /notification-preferences

POST   /support/cases
GET    /support/cases
GET    /support/cases/{case_id}
POST   /support/cases/{case_id}/messages
POST   /support/cases/{case_id}/actions
```

Support actions use separate scopes, just-in-time elevation, reason codes, field
masking, and immutable audits. Generic impersonation is prohibited.

## Provider and webhook APIs

```text
POST /webhooks/amadeus
POST /webhooks/stripe
POST /webhooks/datafast
POST /webhooks/notifications/{provider}

GET  /api/v1/admin/providers
POST /api/v1/admin/providers/{provider_id}/health-checks
GET  /api/v1/admin/webhook-deliveries
POST /api/v1/admin/webhook-deliveries/{delivery_id}/replays
```

Webhook endpoints are not customer APIs. They verify the raw signed request,
persist an immutable delivery envelope, acknowledge quickly, and enqueue
idempotent processing. Administrative replay creates a new audited attempt
without altering the original delivery.

## Operations and governance

```text
GET /health/live
GET /health/ready
GET /health/startup
GET /metrics
GET /api/v1/operations/{operation_id}
```

Metrics require network and identity controls and must not expose user labels.
OpenAPI documents are linted for authentication, error, pagination, idempotency,
PII, and breaking-change rules. Provider adapters have separate contract suites.
