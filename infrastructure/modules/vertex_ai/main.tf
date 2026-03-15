# infrastructure/modules/vertex_ai/main.tf: Vertex AI Search & Vector Search Setup

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "env" {
  type = string
}

# 1. Enable Discovery Engine API explicitly (Safe measure)
resource "google_project_service" "discovery_engine" {
  project = var.project_id
  service = "discoveryengine.googleapis.com"
  disable_on_destroy = false
}

resource "random_id" "datastore_suffix" {
  byte_length = 4
}

# 2. Vertex AI Search Data Store
resource "google_discovery_engine_data_store" "rag_data_store" {
  project                     = var.project_id
  location                    = "global"
  data_store_id               = "rag-docs-${var.env}-${random_id.datastore_suffix.hex}"
  display_name                = "RAG Document Store (${var.env})"
  industry_vertical           = "GENERIC"
  content_config              = "CONTENT_REQUIRED"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]

  depends_on = [google_project_service.discovery_engine]

  lifecycle {
    create_before_destroy = true
  }
}

# 2. BigQuery Dataset for Feedback & Tracing
resource "google_bigquery_dataset" "feedback_dataset" {
  project    = var.project_id
  dataset_id = "agent_feedback"
  location   = var.region
}

output "data_store_id" {
  value = google_discovery_engine_data_store.rag_data_store.data_store_id
}
