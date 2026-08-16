terraform {
  # Remote state is configured via `terraform init -backend-config=...`.
  # See `backend.hcl.example` and `README.md`.
  backend "gcs" {}
}
