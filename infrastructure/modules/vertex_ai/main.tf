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

resource "random_id" "datastore_suffix" {
  byte_length = 4
  keepers = {
    # Force a new ID if we are stuck in a deletion loop
    version = "v26" 
  }
}

# 2. Vertex AI Search Data Store
# Using a random suffix to avoid "being deleted" conflicts.
resource "google_discovery_engine_data_store" "rag_data_store" {
  project                     = var.project_id
  location                    = "global"
  data_store_id               = "rag-docs-${var.env}-${random_id.datastore_suffix.hex}"
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

# 4. BigQuery Table for User Feedback (Thumbs up/down)
resource "google_bigquery_table" "user_feedback" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.feedback_dataset.dataset_id
  table_id   = "user_feedback"
  deletion_protection = false

  schema = <<EOF
[
  {"name": "message_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "rating", "type": "STRING", "mode": "REQUIRED"},
  {"name": "user_email", "type": "STRING", "mode": "NULLABLE"},
  {"name": "comment", "type": "STRING", "mode": "NULLABLE"},
  {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"}
]
EOF
}

# 5. BigQuery Table for Full Conversation Traces
resource "google_bigquery_table" "conversations" {
  project    = var.project_id
  dataset_id = google_bigquery_dataset.feedback_dataset.dataset_id
  table_id   = "conversations"
  deletion_protection = false

  schema = <<EOF
[
  {"name": "query", "type": "STRING", "mode": "REQUIRED"},
  {"name": "response", "type": "STRING", "mode": "REQUIRED"},
  {"name": "user_email", "type": "STRING", "mode": "NULLABLE"},
  {"name": "metadata", "type": "STRING", "mode": "NULLABLE"},
  {"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"}
]
EOF
}

output "data_store_id" {
  value = google_discovery_engine_data_store.rag_data_store.data_store_id
}
