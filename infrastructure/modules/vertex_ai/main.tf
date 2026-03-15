# infrastructure/modules/vertex_ai/main.tf

variable "project_id" { type = string }
variable "region" { type = string }
variable "env" { type = string }

# 1. Enable Discovery Engine API explicitly
resource "google_project_service" "discovery_engine" {
  project = var.project_id
  service = "discoveryengine.googleapis.com"
  disable_on_destroy = false
}

# 2. Vertex AI Search Data Store
# Using a fixed ID per environment to stop the random suffix recreation loop.
resource "google_discovery_engine_data_store" "rag_data_store" {
  project                     = var.project_id
  location                    = "global"
  data_store_id               = "rag-docs-${var.env}-v5"
  display_name                = "RAG Document Store (${var.env})"
  industry_vertical           = "GENERIC"
  content_config              = "CONTENT_REQUIRED"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]

  depends_on = [google_project_service.discovery_engine]
}

# 3. BigQuery Dataset for Feedback & Tracing
resource "google_bigquery_dataset" "feedback_dataset" {
  project    = var.project_id
  dataset_id = "agent_feedback"
  location   = var.region
}

output "data_store_id" {
  value = google_discovery_engine_data_store.rag_data_store.data_store_id
}
