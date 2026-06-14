# Consumer travel marketplace product requirements

## Product decision

The application is a consumer travel marketplace, not a corporate approval
system. It supports:

- **Individual:** a traveler plans and purchases for themselves or companions.
- **Business:** a consumer or managed account can retain receipts, traveler
  profiles, cost centers, and optional organization rules.
- **Group:** an organizer coordinates travelers, rooms, transport, guide
  contacts, shared payments, and participant consent.
- **Support:** authorized agents resolve booking, payment, identity, and
  accessibility cases without unrestricted impersonation.
- **Administration and operations:** tightly scoped staff manage providers,
  content, risk, disputes, reconciliation, and platform health.

The original corporate policy engine is retained only as reusable deterministic
guardrail logic. Manager approval is not the default consumer journey.

## Experiences and dashboards

### Public and account access

- Public destination/search pages with no sensitive itinerary data.
- Sign up, sign in, sign out, email verification, MFA/passkeys, OAuth/OIDC
  federation, consent capture, session/device management, and secure recovery.
- Guest search and optional guest checkout with account linking after purchase.
- Bot and account-takeover protection with accessible challenge alternatives.

### Individual dashboard

- Traveler profiles, loyalty program identifiers, saved preferences, consent,
  accessibility needs, documents metadata, trips, carts, orders, payments,
  refunds, credits, notifications, and support cases.
- Never store raw card data. Avoid passport storage until a booking provider
  contract, retention schedule, encryption design, and access review require it.

### Business dashboard

- Organization membership, traveler/delegate relationships, billing profiles,
  receipt export, cost center/project references, optional budgets and travel
  rules, and role-scoped administration.
- Business features must not leak into or block the ordinary consumer journey.

### Group dashboard

- Organizer and participant roles; invitations and consent; rooming list;
  traveler manifests; per-person allocation; split/shared payments; deadlines;
  change history; and guide details.
- Tour guide fields: first name, last name, organization, email, phone with
  international country code, preferred contact channel, language, availability,
  emergency designation, and explicit consent to share details.

### Support dashboard

- Queues for booking failures, schedule changes, payment attempts, refunds,
  chargebacks, fraud review, webhook failures, abandoned carts, and accessibility
  assistance.
- Just-in-time elevated access, reason codes, field masking, no raw secret or
  payment credential access, immutable audit events, and customer-visible case
  history where appropriate.

## End-to-end trip journey

1. Create, edit, duplicate, save, share, and submit a trip.
2. Capture traveler/companion identity and contact details with consent.
3. Validate origin/destination as airport, city, station, hotel, or address.
4. Capture local dates, time zones, flexible dates, one-way/round-trip/multi-city
   routes, passenger ages, residency, purpose (personal/business/group),
   accessibility needs, baggage, cabin, room, and ground-transport preferences.
5. Search with a canonical query and a provider request correlation ID.
6. Normalize Amadeus responses into canonical offers without losing the original
   supplier payload or terms.
7. Show comparable results: total price, currency, taxes, fees, baggage,
   fare/room rules, refundability, change penalties, accessibility evidence,
   carbon estimate source, supplier, freshness, and expiration.
8. Rank with transparent user-controlled criteria. Clearly label sponsored
   placement and AI involvement; never fabricate inventory or prices.
9. Reprice and verify availability immediately before selection and purchase.
10. Collect traveler confirmation, required supplier data, and explicit
    acceptance of terms and cancellation rules.
11. Create one canonical cart/order and idempotent provider reservations.
12. Authorize/capture payment only for the verified order amount.
13. Display booking status, supplier confirmation/PNR references, itinerary,
    receipts, tickets/vouchers, disruption alerts, and support options.
14. Support eligible changes, cancellation, voids, refunds, credits, and
    provider reconciliation.

## Amadeus integration boundary

- Start with the Amadeus test environment and verify which Self-Service or
  Enterprise APIs, markets, airlines, hotels, ticketing rights, and commercial
  agreements are required before advertising bookable inventory.
- Implement OAuth token caching/refresh, quotas, timeouts, retries with jitter,
  circuit breaking, schema/version validation, response-size limits, redaction,
  idempotency, and request/response correlation.
- Separate flight inspiration/search, offer pricing, traveler validation,
  booking/order creation, hotel search/booking, airport/location lookup, flight
  status, and cancellation capabilities.
- Treat an offer as expiring inventory. Store provider offer ID, retrieval time,
  expiry, price guarantee status, and the exact accepted terms.
- Design degraded behavior for provider outage and partial booking. Never report
  `BOOKED` until authoritative provider confirmation is persisted.
- Add alternate travel suppliers only through the same internal provider
  protocols; do not couple the domain model to Amadeus payloads.

## Commerce, tax, and payment platform

### Canonical ledger

Every quote, cart, order, payment, refund, and reconciliation entry uses integer
minor units plus ISO currency. Keep immutable line items for:

- Base reservation price per flight, room, vehicle, transfer, activity, or fee.
- Supplier taxes and government taxes by jurisdiction and responsible party.
- Platform/service fees, payment fees where legally displayable, discounts,
  credits, insurance, tips, commissions, and foreign-exchange rate/markup.
- Per-traveler and shared allocations.
- Authorized, captured, refunded, disputed, settled, and outstanding totals.
- Tax/fee source, calculation timestamp, evidence, and rounding adjustments.

The customer sees the full total before payment and receives an itemized receipt.
Accounting also needs a double-entry ledger, settlement reports, payout matching,
chargeback tracking, and provider-versus-platform reconciliation.

### Provider-neutral payments

- Define `PaymentProvider` and `PaymentMethod` contracts for intent/session
  creation, customer action, authorization, capture, void, refund, status,
  dispute, and signed webhook verification.
- Implement Stripe and Datafast as independent adapters. Select availability by
  country, currency, merchant entity, risk, and payment method—not by UI code.
- Keep future carts/wallets and bank methods pluggable. Use hosted/tokenized
  fields; the platform must never receive PAN or CVV.
- Use one idempotency key per logical operation, bind payment amount/currency to
  the server-side order, and prevent duplicate capture and refund.
- Support 3-D Secure/SCA where applicable, delayed/asynchronous methods, payment
  failure recovery, partial/multiple refunds, disputes, chargebacks, and
  abandoned checkout recovery with consent-aware communications.
- Determine merchant-of-record, seller-of-travel, tax, invoicing, payout,
  refund, and chargeback responsibilities with legal and finance before launch.

### UCP

UCP is an interoperability adapter, not the internal order model. Implement
version negotiation, capability discovery, minor-unit amounts, authenticated
principal-to-agent binding, HTTP message signature verification, replay
protection, checkout/order mapping, and human confirmation. Keep autonomous
purchase disabled until scoped mandates, amount/currency limits, expiry,
revocation, and complete audit evidence are implemented.

## Webhooks, notifications, and fraud

### Webhook standard

- Dedicated HTTPS endpoints per provider and environment.
- Verify signatures against the raw body; rotate versioned secrets/keys.
- Enforce timestamp tolerance, event-ID deduplication, replay protection,
  content type and body limits, schema/version validation, and provider IP
  filtering only as defense in depth.
- Acknowledge quickly, persist first, process asynchronously, retry with
  exponential backoff and jitter, dead-letter poison events, and expose replay
  tooling to authorized operators.
- Preserve ordering metadata but make handlers idempotent and tolerant of
  duplicates and out-of-order delivery.
- Correlate webhook, order, payment, provider request, trace, and audit IDs.

### Customer notifications

- In-app notification center plus opt-in email, SMS, and push channels.
- Events include verification, login/security alerts, price/availability
  changes, cart expiration, abandoned cart, payment action/failure/success,
  booking confirmation/failure, ticket issuance, schedule disruption,
  cancellation, refund, dispute, and support updates.
- Separate transactional from marketing consent; support preferences,
  localization, quiet hours, delivery receipts, retries, unsubscribe, retention,
  and provider failover.
- Never place full itinerary, sensitive identity data, tokens, or payment
  details in notification previews.

### Fraud and abuse

- Account/device velocity, impossible travel, credential stuffing, promo abuse,
  bot search, card testing, payment mismatch, repeated failures, chargeback
  history, high-risk itinerary, and webhook anomalies.
- Rules and model scores produce explainable risk evidence and route to allow,
  step-up, 3DS, hold/manual review, or deny. The AI concierge cannot override
  these decisions.
- Add case management, false-positive review, customer appeal, sanctions/legal
  review where applicable, model drift/bias monitoring, and retained decision
  evidence.

## Cloud and delivery architecture

- **Cloud Run:** stateless web/API, worker, and webhook receiver services with
  separate service accounts, minimum instances only where justified, bounded
  concurrency, timeouts, health checks, and private egress where possible.
- **Cloud SQL PostgreSQL:** canonical transactional state; migrations, PITR,
  backups, restore drills, connection pooling, and regional recovery objectives.
- **Pub/Sub and Cloud Tasks:** durable events, delayed retries, notification
  delivery, booking orchestration, and webhook processing.
- **Secret Manager + Cloud KMS:** provider credentials and envelope-encryption
  keys; no secrets in images, source, Cloud Build substitutions, logs, or AI
  prompts.
- **Cloud Build/Artifact Registry:** reproducible builds, provenance/SBOM,
  signing, vulnerability gates, migration validation, staged deployment, smoke
  tests, canary/rollback, and separated build/deploy identities.
- **Cloudflare:** DNS, TLS, WAF, bot/rate controls, DDoS protection, and caching
  only for explicitly public assets. Never cache account, checkout, itinerary,
  support, or webhook responses. Document origin authentication and real-client
  IP trust.
- Use Infrastructure as Code, separate projects/accounts for development,
  staging, and production, budgets/quotas, data residency decisions, and tested
  disaster recovery.
- **Firebase:** use Firebase Authentication as an OIDC-capable customer identity
  provider, Cloud Messaging for push delivery, App Check as an abuse signal, and
  consent-gated Analytics/Crashlytics where approved. PostgreSQL and the FastAPI
  domain remain authoritative for trips, orders, payments, audit, and support;
  Firestore is not a parallel booking database.
- **Flutter:** provide one adaptive client for Android, iOS, and web using the
  versioned REST API. Keep domain rules, provider credentials, trusted totals,
  authorization, fraud decisions, and booking confirmation on the server.

### Terraform

- Terraform is the authoritative infrastructure definition for GCP and
  Cloudflare resources. Keep state in a versioned, encrypted remote backend with
  locking, retention, restricted IAM, and a documented break-glass process.
- Use separate state and projects/accounts for development, staging, and
  production. Do not select environments only through Terraform workspaces.
- Pin Terraform and provider versions; commit dependency locks; run `fmt`,
  `validate`, lint, policy, security, cost, and plan checks on pull requests.
- Plans must use short-lived workload identity federation, require approval for
  production apply, preserve plan artifacts, redact sensitive output, and detect
  drift on a schedule. CI must never use long-lived service-account keys.
- Split reusable modules by responsibility: project services, IAM/service
  accounts, Artifact Registry, Cloud Run, Cloud SQL, networking/egress, Pub/Sub,
  Cloud Tasks, KMS, Secret Manager, monitoring, budgets, and Cloudflare edge.
- Enforce deletion protection, backups, point-in-time recovery, least privilege,
  labels, audit logging, ingress/egress constraints, and environment-specific
  policy as code. Import existing resources before management; never recreate a
  production database to resolve drift.

## API platform

- Publish versioned REST APIs under `/api/v1`; generate and validate OpenAPI,
  client SDKs, and contract tests in CI. Do not expose provider-native payloads
  as public contracts.
- Use RFC 9457 problem details, request/correlation/trace IDs, cursor pagination,
  explicit API and schema versions, bounded filtering/sorting, content-type and
  body-size validation, and ISO dates/currencies.
- Mutation endpoints require idempotency keys and optimistic concurrency where
  stale updates are dangerous. Long-running work returns a job or operation
  resource rather than holding a request open.
- Maintain separate public/customer, partner/provider-webhook, support, and
  administration surfaces with independent OAuth audiences, scopes, quotas,
  audit policies, and network controls.
- Apply authorization to every resource, field, and action. A UUID, booking
  locator, email address, or provider reference is never proof of access.
- Version additively when possible; publish deprecation and sunset headers,
  migration guidance, changelogs, support windows, and consumer-driven contract
  tests before removing behavior.
- Provide sandbox credentials, mock providers, deterministic fixtures, rate-limit
  headers, retry guidance, and a status page. Never make CI depend on live paid
  Amadeus, payment, messaging, or model APIs.

Required resource families are detailed in `docs/api-contracts.md`.

## Firebase and Flutter

- Maintain separate Firebase projects and application registrations for
  development, staging, and production. Never reuse production API keys,
  signing identities, APNs credentials, or service accounts in lower
  environments.
- Generate `firebase_options.dart` with FlutterFire tooling per environment and
  keep secrets out of Dart defines, bundles, source maps, repositories, and
  crash reports. Firebase client API keys identify projects but are not
  authorization controls.
- Exchange and validate Firebase ID tokens at the FastAPI boundary. Validate
  signature, issuer, audience, expiry, revocation where required, and server-side
  user status. Custom claims are coarse role hints only; ownership and
  relationships still come from the application database.
- Require email verification and support MFA/passkeys as product risk requires.
  Protect account linking, provider changes, recovery, deletion, and sensitive
  actions against session fixation and account takeover.
- Register FCM tokens per installation and user, rotate/delete stale tokens,
  avoid sensitive notification payloads, respect consent and quiet hours, and
  deep-link only through validated allowlisted routes.
- Treat App Check as defense in depth, not user authentication. Enforce API
  authorization, rate limits, replay protection, and fraud controls even when an
  App Check token is valid.
- Flutter state must distinguish public cache, session state, and sensitive trip
  data. Encrypt only narrowly justified local data, use OS secure storage for
  refresh/session material, and clear protected data on logout or revocation.
- Meet WCAG 2.2 AA-equivalent mobile accessibility expectations: semantic
  labels, dynamic text, screen-reader order, keyboard support on web/desktop,
  high contrast, reduced motion, minimum touch targets, and accessible errors.
- Test unit, widget, golden, integration, deep-link, offline/retry, localization,
  authentication, App Check, notification, accessibility, and release-signing
  behavior. Use Firebase Emulator Suite and mocked APIs in CI.

The integration boundary and setup sequence are in `docs/firebase-flutter.md`.

## Model Context Protocol (MCP)

- MCP is an optional, separately deployable tool boundary for authorized
  assistants and operator tooling. It is not an alternative authentication
  mechanism, API gateway, booking state machine, or payment authorization path.
- Expose narrowly scoped, typed tools over canonical application services; never
  expose arbitrary SQL, shell execution, unrestricted HTTP fetch, secrets,
  payment credentials, raw provider tokens, or unrestricted file access.
- Separate read-only customer tools, customer-confirmed mutation tools, and
  privileged support/operations tools into different servers or policy domains.
- Bind every call to an authenticated principal, OAuth audience/scope, tenant or
  account context, resource ownership, current trip/order state, consent, and a
  short-lived correlation ID. Never trust identity or role arguments supplied by
  the model.
- Require structured schemas, bounded inputs/outputs, allowlisted enumerations,
  output redaction, rate/cost limits, timeouts, idempotency, human confirmation
  for consequential actions, and immutable audit evidence.
- Treat tool descriptions, resources, prompts, supplier text, and model output as
  untrusted. Defend against prompt injection, confused deputy, cross-user data
  access, tool poisoning, SSRF, replay, and excessive agency.
- Version server capabilities and tool schemas; support client capability
  negotiation, revocation, kill switches, deterministic fallback, conformance
  tests, red-team tests, and telemetry without sensitive prompt logging.

The initial MCP catalog and prohibited capabilities are in `docs/mcp.md`.

## Identity, authorization, and encryption

- Use OAuth 2.0 Authorization Code with PKCE and OIDC for user identity. OAuth
  authorization and authentication are distinct; validate issuer, audience,
  nonce, state, redirect URI, and token lifetime.
- Prefer passkeys and MFA; provide secure recovery, session revocation, breached
  credential controls, login throttling, and security event notifications.
- Combine RBAC with ownership/relationship checks: `individual`, `organizer`,
  `business_member`, `business_admin`, `guide`, `support_l1`, `support_l2`,
  `fraud_analyst`, `finance`, `content_admin`, `platform_admin`, and `auditor`.
  Deny by default and prevent role self-assignment.
- Use workload identity and least-privilege IAM for services. Human cloud access
  requires SSO, MFA, just-in-time elevation, approval, and audit.
- TLS 1.2+ in transit and provider-managed encryption at rest are baselines.
  Use application-level envelope encryption for selected PII, Cloud KMS key
  versions and rotation, Secret Manager for credentials, and documented
  cryptographic deletion. AES-256 is an implementation option, not by itself a
  complete encryption program.
- GitHub/GitLab protects source and CI metadata; it must not be the production
  secret store or primary application encryption boundary.

## AI concierge: Vertex and Gemma 4

- Place `PlanningModel` behind a provider-neutral interface. Gemma 4 on Vertex AI
  or Cloud Run is optional; deterministic search, pricing, authorization,
  checkout, fraud, and booking continue when it is unavailable.
- AI may interpret preferences, explain normalized offers, summarize itinerary
  changes, translate support content, and propose reversible actions.
- AI may not invent availability/price, choose arbitrary URLs, access payment
  credentials, approve risk exceptions, confirm a booking, or submit a purchase
  without explicit validated user confirmation.
- Ground only on structured canonical data. Treat traveler notes, supplier text,
  webpages, and documents as untrusted prompt-injection sources.
- Record model/prompt/tool versions, consent, citations to source offers,
  latency/cost, safety outcomes, and human confirmation without logging sensitive
  prompts. Add evaluation suites, red teaming, drift monitoring, output schemas,
  tool allowlists, rate/cost limits, kill switch, and a non-AI fallback.

## Requirements that are easy to forget

1. **Commercial authority:** Amadeus production access, ticketing/accreditation,
   market coverage, supplier contracts, and who services disrupted bookings.
2. **Merchant/legal roles:** merchant of record, seller-of-travel registration,
   terms of sale, privacy notice, cookie consent, refund policy, chargebacks,
   insurance licensing, sanctions, and consumer-protection obligations.
3. **Inventory lifecycle:** repricing, expiration, schedule changes, exchanges,
   void windows, partial cancellation, no-shows, split PNRs, and partial booking.
4. **Traveler edge cases:** infants/children, unaccompanied minors, names matching
   documents, nationality/residency, visas/passports, special service requests,
   pets, loyalty programs, emergency contacts, and accessibility confirmation.
5. **Money operations:** multi-currency display versus settlement, FX disclosure,
   rounding, tax evidence, commissions, payouts, reconciliation, disputes,
   credits, vouchers, and financial record retention.
6. **Privacy lifecycle:** data inventory, purpose/consent, minimization, residency,
   retention/deletion, export/correction, subprocessors, breach response, and
   protections for children and sensitive accessibility data.
7. **Support operations:** 24/7 ownership for active travel, escalation, SLAs,
   supplier contact paths, status page, customer compensation, and runbooks.
8. **Reliability:** SLOs, capacity/load tests, quota exhaustion, provider
   failover, RTO/RPO, backup restore tests, chaos scenarios, and cost controls.
9. **Trustworthy marketplace UX:** clear seller/provider identity, freshness,
   full price, terms, sponsored ranking, dark-pattern prohibition, review before
   purchase, and accessible recovery from every failure.
10. **SEO/PWA/i18n:** localized routes and metadata, schema.org travel markup,
    Core Web Vitals, offline public shell only, no sensitive caching, locale/time
    zone/currency formatting, RTL readiness, and WCAG 2.2 AA validation.

## Delivery order

1. Canonical consumer domain: identity, traveler, trip, offer, cart, order,
   ledger, payment, booking, notification, support case, and audit.
2. Persistence, migrations, state machines, idempotency, outbox, and worker.
3. OAuth/OIDC, MFA/passkeys, relationship authorization, and support RBAC.
4. Seeded provider simulators and an end-to-end non-AI checkout test.
5. Amadeus search/reprice sandbox adapter and contract tests.
6. Stripe sandbox adapter, then Datafast sandbox adapter, signed webhooks,
   ledger, reconciliation, and refund tests.
7. Accessible customer, group, business, and support interfaces.
8. Cloud Run/Cloud Build/Cloud SQL deployment with Cloudflare edge controls.
9. Terraform modules, remote state bootstrap, policy/security checks, and
   workload-identity-based plan/apply pipelines.
10. Versioned API contracts, SDK/contract tests, partner sandbox, and operational
    API governance.
11. Fraud, notifications, operations, privacy, and compliance evidence.
12. Firebase Authentication/FCM/App Check and the Flutter customer shell, first
    against emulators and deterministic API fixtures.
13. Optional MCP, UCP, and Gemma 4 integrations after deterministic commerce is
    safe.

Production remains blocked until legal/commercial responsibilities, provider
contracts, authentication, authorization, persistence, payment scope, webhook
security, audit, privacy operations, and recovery tests are complete.
