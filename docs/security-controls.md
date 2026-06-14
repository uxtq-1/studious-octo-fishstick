# Security controls status

This reconstruction is **not certified or assessed as compliant** with NIST CSF, CISA Cyber Essentials, PCI DSS, GDPR, or CCPA. It is a development foundation.

| Control area | Status | Evidence / limitation |
|---|---|---|
| Source provenance | Implemented | Original artifacts preserved and mapped |
| Deterministic financial guardrails | Partially implemented | Decimal limits; no persistence, tax engine, or currency conversion |
| Authentication and authorization | Planned | No sensitive workflow endpoints are enabled |
| Payment-data handling | Not applicable in this phase | No payment endpoint and no PAN/CVV fields |
| Simulation disclosure | Implemented | UI and API description explicitly disclose demonstration mode |
| Dependency/static analysis | Partially implemented | CI jobs configured; repository settings must enforce checks |
| Audit logging and tamper evidence | Planned | Requires persistence phase |
| Merchant SSRF protection | Planned | No outbound merchant calls are enabled |
| OAuth 2.0/OIDC and MFA | Planned | Identity provider and account recovery are not implemented |
| RBAC and ownership checks | Planned | Individual, business, group, support, and administrator scopes are specified only |
| Webhook authenticity/replay defense | Planned | Stripe, Datafast, and Amadeus callbacks are not connected |
| Encryption and key management | Planned | Requires Cloud KMS/Secret Manager design and rotation procedures |
| Fraud and abuse controls | Planned | Risk signals, 3DS/SCA routing, velocity rules, and case review are not implemented |
