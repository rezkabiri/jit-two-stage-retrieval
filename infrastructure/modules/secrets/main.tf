# infrastructure/modules/secrets/main.tf

variable "project_id" { type = string }
variable "env" { type = string }
variable "gemini_api_key" { 
  type      = string 
  sensitive = true
}
variable "service_account_email" { type = string }

# 1. Enable Secret Manager API
resource "google_project_service" "secretmanager" {
  project            = var.project_id
  service            = "secretmanager.googleapis.com"
  disable_on_destroy = false
}

# 2. Create the Secret container
resource "google_secret_manager_secret" "gemini_api_key" {
  project   = var.project_id
  secret_id = "gemini-api-key-${var.env}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.secretmanager]
}

# 3. Add the Secret Version
resource "google_secret_manager_secret_version" "gemini_api_key_version" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key
}

# 4. Grant Access to the Cloud Run Service Account
resource "google_secret_manager_secret_iam_member" "accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.gemini_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.service_account_email}"
}

output "secret_id" {
  value = google_secret_manager_secret.gemini_api_key.secret_id
}

output "secret_name" {
  value = google_secret_manager_secret.gemini_api_key.name
}
