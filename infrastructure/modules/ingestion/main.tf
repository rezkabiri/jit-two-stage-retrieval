# infrastructure/modules/ingestion/main.tf: RAG Ingestion Cloud Function & IAM

# 1. Enable Required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "cloudfunctions.googleapis.com",
    "eventarc.googleapis.com",
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "pubsub.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com"
  ])
  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# 2. Service Identities (Required for 2nd Gen Triggers)
# Eventarc identity
resource "google_project_service_identity" "eventarc_identity" {
  provider = google-beta
  project  = var.project_id
  service  = "eventarc.googleapis.com"
  
  depends_on = [google_project_service.apis]
}

# Storage identity (for Pub/Sub publishing)
data "google_storage_project_service_account" "gcs_account" {
  project = var.project_id
}

# 3. IAM Permissions
# A. Storage Service Account to Pub/Sub Publisher
resource "google_project_iam_member" "storage_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${data.google_storage_project_service_account.gcs_account.email_address}"
}

# B. Eventarc Service Agent
resource "google_project_iam_member" "eventarc_service_agent" {
  project = var.project_id
  role    = "roles/eventarc.serviceAgent"
  member  = "serviceAccount:${google_project_service_identity.eventarc_identity.email}"
}

# C. Dedicated Trigger Service Account
# Using a dedicated SA for the trigger is more reliable than the service agent identity for invocation
resource "google_service_account" "trigger_sa" {
  account_id   = "rag-trigger-sa-${var.env}"
  display_name = "RAG Trigger Service Account (${var.env})"
  project      = var.project_id
}

# Grant Trigger SA permission to receive events
resource "google_project_iam_member" "trigger_receiver" {
  project = var.project_id
  role    = "roles/eventarc.eventReceiver"
  member  = "serviceAccount:${google_service_account.trigger_sa.email}"
}

# Grant Trigger SA permission to invoke the Cloud Run service (Fixes 403)
resource "google_cloud_run_v2_service_iam_member" "trigger_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloudfunctions2_function.ingestion_function.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.trigger_sa.email}"
}

# D. Runtime Service Account (Defaulting to Compute Engine SA for simplicity)
data "google_project" "project" {
  project_id = var.project_id
}

locals {
  compute_sa = "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}

# Grant Vertex AI Editor role to the runtime SA (for indexing)
resource "google_project_iam_member" "vertex_ai_editor" {
  project = var.project_id
  role    = "roles/discoveryengine.editor"
  member  = "serviceAccount:${local.compute_sa}"
}

# Grant Storage Object Viewer role to the runtime SA (to download files)
resource "google_project_iam_member" "storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${local.compute_sa}"
}

# 4. Source Code Archive (Zipping the ingestion folder)
# We'll use a local zip file and upload it to the ingestion bucket for now
data "archive_file" "ingestion_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../../data-pipeline/ingestion"
  output_path = "/tmp/ingestion-${var.env}.zip"
}


resource "google_storage_bucket_object" "source_code" {
  name   = "ingestion-src-${data.archive_file.ingestion_zip.output_md5}.zip"
  bucket = var.ingestion_bucket_name
  source = data.archive_file.ingestion_zip.output_path
}

# 5. Cloud Function (2nd Gen)
resource "google_cloudfunctions2_function" "ingestion_function" {
  name        = "rag-ingestion-${var.env}"
  location    = var.region
  project     = var.project_id
  description = "RAG Automated Ingestion Pipeline (${var.env})"

  build_config {
    runtime     = "python311"
    entry_point = "process_gcs_upload"
    source {
      storage_source {
        bucket = var.ingestion_bucket_name
        object = google_storage_bucket_object.source_code.name
      }
    }
  }

  service_config {
    max_instance_count = 3
    available_memory   = "512Mi"
    timeout_seconds    = 120
    
    all_traffic_on_latest_revision = true

    environment_variables = {
      GOOGLE_CLOUD_PROJECT = var.project_id
      DATA_STORE_ID        = var.data_store_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.storage.object.v1.finalized"
    retry_policy   = "RETRY_POLICY_RETRY"
    service_account_email = google_service_account.trigger_sa.email
    event_filters {
      attribute = "bucket"
      value     = var.ingestion_bucket_name
    }
  }
  
  lifecycle {
    ignore_changes = [
      service_config[0].environment_variables,
    ]
  }

  depends_on = [
    google_project_iam_member.storage_pubsub_publisher,
    google_project_iam_member.eventarc_service_agent,
    google_project_iam_member.trigger_receiver
  ]
}
