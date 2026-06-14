# Model Context Protocol boundary

MCP may make the marketplace accessible to approved assistants, but it must not
grant authority that the authenticated user or operator does not already have.
MCP servers call the same application services and policy enforcement points as
REST and HTML routes.

## Initial server separation

| Server | Audience | Examples | Mutation policy |
|---|---|---|---|
| Travel discovery | Authenticated customer | Search airports, create search, list normalized offers, explain terms | Search only; bounded cost and rate |
| Trip assistant | Trip owner, delegate, or organizer | Read trip, compare selected offers, summarize itinerary | Selection requires explicit confirmation |
| Order assistant | Order owner | Read cart/order/payment status, request cancellation quote | Checkout, cancellation, or refund requires step-up and confirmation |
| Support assistant | Authorized support role | Read masked case context, add case note, execute an approved runbook action | JIT elevation, reason code, audit, and action allowlist |
| Operations | On-call/operator role | Provider health, failed webhook/job metadata, safe replay request | Separate server and audience; no customer assistant access |

## Candidate tool catalog

```text
locations.search
trips.create_draft
trips.get
trips.update_preferences
offers.search
offers.list
offers.compare
carts.get
carts.request_price_verification
orders.get
itineraries.get
cancellations.quote
support_cases.create
support_cases.get
notifications.preferences_get
notifications.preferences_update
```

Consequential tools such as `orders.confirm`, `payments.authorize`,
`cancellations.confirm`, `refunds.request`, webhook replay, or support account
recovery remain disabled until their consent ceremony, authorization, state,
idempotency, risk, and audit tests are complete.

## Required call context

The MCP gateway derives, signs, and forwards:

- Subject and session identifiers.
- OAuth issuer, audience, scopes, and authentication strength.
- Account/organization/group relationships.
- Correlation and trace IDs.
- Tool and schema version.
- Consent/confirmation artifact when required.

Models and clients cannot override these fields. Tool arguments contain only the
resource IDs and bounded domain data needed for the action.

## Security and privacy controls

- Deny by default; authorize each resource and action after schema validation.
- Use short-lived credentials, audience restriction, rotation, and revocation.
- Sanitize supplier/user content and isolate it from system/tool instructions.
- Reject arbitrary URLs and block private, loopback, link-local, metadata, and
  non-allowlisted destinations at every network boundary.
- Limit response records, bytes, execution time, tool chaining depth, tokens,
  and monetary/search cost.
- Redact PII according to role and purpose. Do not return secrets, full payment
  data, raw identity documents, hidden fraud signals, or provider credentials.
- Record subject, tool, resource, schema version, policy decision, confirmation,
  outcome, latency, and redacted error—not private reasoning or sensitive prompt
  content.
- Add per-tool conformance tests for cross-user access, prompt injection,
  confused deputy, replay, duplicate mutation, stale state, SSRF, poisoned tool
  descriptions, overbroad output, cancellation, and provider failure.

## Availability and change management

REST APIs and direct web workflows remain available when MCP or a model is
disabled. Servers advertise versioned capabilities; incompatible changes create
new tool versions. Operations can revoke a tool, provider, client, model, or
server independently through a tested kill switch.
