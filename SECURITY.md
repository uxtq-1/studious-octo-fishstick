# Security policy

## Supported versions

Only the latest commit on the default branch is supported during this
development phase. The application is a demonstration and is not approved for
real bookings, passenger documents, or payment-card processing.

## Reporting a vulnerability

Do not disclose vulnerabilities, personal data, credentials, provider details,
private URLs, or exploit instructions in a public issue.

Use the repository host's private security-advisory feature. If that feature is
unavailable, contact the designated security team through the private security
contact configured by the repository owner:

`security-contact-to-be-configured`

Include affected versions, reproducible steps, impact, and suggested mitigation.
Allow reasonable time for investigation before public disclosure.

## Security baseline

The project is designed to align with NIST CSF 2.0, NIST SP 800-53 Rev. 5,
NIST SP 800-218 SSDF, CISA Cybersecurity Performance Goals, OWASP Top 10, OWASP
API Security Top 10, OWASP ASVS, OWASP MASVS for Flutter, and PCI DSS v4.0.1
where payment responsibilities apply. This is a control target, not a claim of
certification or compliance.

Implemented foundations include conservative browser headers, allowlisted CORS,
trusted hosts, request-size and media-type controls, safe public authorization
errors, role/tenant/owner authorization primitives, structured audit redaction,
outbound URL validation, webhook HMAC/timestamp validation, and security tests.

## Payment and privacy boundary

The application must never collect, store, or log PAN, CVV, magnetic-stripe
data, authentication secrets, raw access tokens, or payment-provider secrets.
Future payment flows must use hosted or tokenized provider interfaces.

Passenger and support data must be minimized, masked by role, encrypted where
appropriate, excluded from URLs and telemetry, retained only for an approved
period, and deleted or exported through authorized workflows.

## Deployment responsibilities

Before production:

- Replace development header authentication with verified OIDC/Firebase tokens,
  MFA for privileged roles, short-lived sessions, and refresh-token rotation.
- Configure explicit production CORS origins and trusted hosts.
- Enforce TLS and HSTS at Cloudflare and Cloud Run; protect the origin from
  direct untrusted traffic.
- Store credentials in Secret Manager and cryptographic keys in Cloud KMS.
- Configure Cloud Armor/Cloudflare WAF, bot controls, shared rate limits, alerting,
  immutable audit retention, database backups, and restore tests.
- Configure Stripe/DataFast and supplier webhook secrets only in secret storage,
  then add provider-specific signature, replay, idempotency, and tenant mapping.
- Enable GitHub/GitLab secret scanning, protected branches, required reviews,
  dependency review, CodeQL, IaC scanning, SBOM generation, and signed artifacts.
