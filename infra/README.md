# CineCritic — Terraform (GCP)

This folder contains Terraform for recreating the Google Cloud pieces of CineCritic (Artifact Registry, Cloud Run, Cloud SQL, etc.).

## Prereqs

- Terraform installed (`terraform version`)
- `gcloud` authenticated (`gcloud auth application-default login`)
- A dedicated GCS bucket to store Terraform state (create once, outside Terraform)

## Bootstrap remote state (one-time)

Pick a globally unique bucket name and create it in your project/region:

```bash
export GCP_PROJECT_ID="your-project-id"
export TF_STATE_BUCKET="your-terraform-state-bucket"
export TF_STATE_REGION="australia-southeast1"

gcloud config set project "$GCP_PROJECT_ID"

gsutil mb -p "$GCP_PROJECT_ID" -l "$TF_STATE_REGION" "gs://$TF_STATE_BUCKET"
gsutil versioning set on "gs://$TF_STATE_BUCKET"
```

## Configure variables

Copy the example tfvars and edit values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars` is ignored by git (local-only).

## Configure remote state backend

Copy the example backend config and edit bucket/prefix:

```bash
cp backend.hcl.example backend.hcl
```

`backend.hcl` is ignored by git (local-only).

## Init / plan

```bash
cd infra
terraform init -backend-config=backend.hcl
terraform fmt
terraform validate
terraform plan
```

## Notes

- The GCS backend cannot read values from Terraform variables; keep bucket/prefix in `backend.hcl` (or pass `-backend-config=key=value` flags).
- Until additional resources are added, `terraform plan` should be empty/no changes.
