# infrastructure/modules/project/main.tf: Project & Registry Setup

variable "project_id" {
  description = "The existing GCP Project ID"
  type        = string
}

# 1. Fetch Existing Project
data "google_project" "project" {
  project_id = var.project_id
}

# 2. Artifact Registry for Container Images
resource "google_artifact_registry_repository" "rag_repo" {
  project       = var.project_id
  location      = "us-central1"
  repository_id = "rag-repo"
  description   = "Docker repository for JIT RAG Agent and UI"
  format        = "DOCKER"
}

output "project_id" {
  value = data.google_project.project.project_id
}

output "project_number" {
  value = data.google_project.project.number
}
