# Terraform foundation

This directory is the initial, non-production Terraform root for Google Cloud.
It enables the APIs and artifact repository needed before Cloud Run services are
defined. It intentionally does **not** create Cloud SQL, networking, secrets,
payment infrastructure, or public services yet.

## Prerequisites

- Terraform 1.8 or newer.
- An existing Google Cloud project and billing account.
- Application Default Credentials or CI workload identity federation.
- A separately bootstrapped, encrypted remote state bucket for shared
  environments. Never commit state or service-account keys.

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -check -recursive
terraform validate
terraform plan
```

Do not run production `apply` from a workstation. CI should save a reviewed plan
and apply that exact artifact after environment approval.

## Next modules

Add independently reviewed modules for service accounts/IAM, Cloud Run,
Cloud SQL, VPC/egress, Pub/Sub, Cloud Tasks, KMS, Secret Manager, monitoring,
budgets, and Cloudflare. Each module must include least privilege, logging,
backup/deletion controls, labels, tests, and import/migration guidance.
