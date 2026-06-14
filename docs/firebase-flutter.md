# Firebase and Flutter integration

## Role in the architecture

Flutter is the customer-facing cross-platform client. Firebase supplies selected
managed client services; it does not replace the FastAPI application, PostgreSQL
transactions, payment providers, Amadeus adapters, or canonical audit log.

| Capability | System of record |
|---|---|
| Customer authentication | Firebase Authentication; application user status and relationships remain in PostgreSQL |
| Trips, offers, carts, orders, payments, refunds | FastAPI services backed by PostgreSQL |
| Push delivery | Firebase Cloud Messaging; notification intent/history remains in the application |
| Mobile/web abuse signal | Firebase App Check plus server rate, fraud, and authorization controls |
| Product analytics/crash diagnostics | Firebase only after consent, minimization, retention, and legal review |
| Static Flutter web assets | Firebase Hosting is optional; Cloudflare may front public assets |

Do not store booking state in Firestore merely to make the Flutter client appear
real-time. Use versioned APIs and authorized event/status channels so every
client sees the same state.

## Environment setup

1. Create separate Google Cloud and Firebase projects for development, staging,
   and production.
2. Register distinct Android, iOS, and web application IDs in each project.
3. Configure authorized authentication domains, OAuth redirect URIs, SHA
   fingerprints, Apple capabilities, APNs keys, and universal/app links.
4. Install FlutterFire tooling locally and generate environment-specific
   `firebase_options.dart`; do not commit a generated production configuration
   until repository policy and deployment ownership are approved.
5. Use the Firebase Emulator Suite for authentication and other supported local
   services. Tests must not call production projects.
6. Configure CI with short-lived workload identity. Do not upload
   service-account JSON keys, signing keys, provisioning profiles, or APNs keys
   into source control.

The committed Flutter shell deliberately compiles without Firebase packages. Add
`firebase_core`, `firebase_auth`, `firebase_app_check`,
`firebase_messaging`, and approved telemetry packages only with generated
configuration, emulator tests, privacy review, and lockfile updates.

## Authentication exchange

1. Flutter signs in through Firebase Authentication.
2. Flutter obtains a short-lived Firebase ID token over TLS.
3. The client sends `Authorization: Bearer <token>` to the FastAPI API.
4. FastAPI verifies the JWT signature and Firebase issuer/audience/expiry and
   resolves the Firebase subject to an internal user.
5. FastAPI applies account status, ownership, relationship, consent, RBAC, and
   state-machine authorization.

The API never trusts email, display name, organization, support role, traveler
relationship, or custom role claims supplied in request bodies. Sensitive
operations can require recent authentication and a server-created confirmation
artifact.

## Notifications

- Store FCM registration tokens as hashed or encrypted installation records with
  platform, user, locale, consent, last-seen, and revocation metadata.
- Send opaque event identifiers, not full itinerary, payment, identity, support,
  or fraud data. Fetch details from the authenticated API after opening.
- Validate every deep link against an allowlist and reauthorize the referenced
  resource. A notification is never proof of access.
- Process token refresh, logout, account deletion, uninstall feedback, invalid
  token responses, retries, deduplication, quiet hours, and channel preferences.

## App Check and web hosting

App Check helps distinguish registered application instances but does not
replace user authentication or API authorization. Roll out in monitor mode,
measure false rejection, support debug providers only in development, and then
enforce per environment and endpoint.

If Firebase Hosting serves Flutter web:

- Cache hashed static assets aggressively.
- Do not cache authenticated API, itinerary, checkout, support, or webhook
  responses.
- Set CSP, HSTS, MIME sniffing, referrer, permissions, and frame controls.
- Route API traffic to the Cloud Run origin through an explicit, protected
  domain; do not embed provider secrets in web builds.

The repository `firebase.json` includes conservative hosting headers and does
not configure rewrites to an undeployed backend.

## Flutter engineering requirements

- Organize by feature with API/domain/data/presentation boundaries.
- Use immutable typed models generated from reviewed OpenAPI schemas.
- Centralize authenticated HTTP, retries, timeout, cancellation, correlation ID,
  error mapping, token refresh, and certificate/platform policy.
- Never log tokens, traveler PII, raw itineraries, payment data, or provider
  payloads. Redact crash breadcrumbs.
- Support adaptive navigation, localization, RTL, dynamic text, screen readers,
  keyboard/focus, reduced motion, high contrast, and offline recovery.
- Avoid storing sensitive responses in browser caches or ordinary preferences.
  Use platform secure storage only for narrowly scoped credentials.
- Require `flutter analyze`, unit/widget tests, dependency/license review,
  secret scanning, release signing verification, and Android/iOS/web builds in
  CI before release.
