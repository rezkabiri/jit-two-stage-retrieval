# infrastructure/modules/cloud_run/main.tf

variable "project_id" { type = string }
variable "region" { type = string }
variable "env" { type = string }
variable "agent_image" { type = string }
variable "ui_image" { type = string }
variable "data_store_id" { type = string }
variable "gemini_api_key_secret_name" { type = string }
variable "user_email" { 
  type        = string
  description = "The email address of the user allowed to invoke the services"
}
variable "location" {
  type        = string
  default     = "global"
  description = "The location of the Vertex AI Data Store (usually global)"
}

# 0. Fetch Project Info (to get project number for IAP Service Agent)
data "google_project" "project" {
  project_id = var.project_id
}

# 0a. Ensure IAP Service Identity exists
resource "google_project_service_identity" "iap_identity" {
  provider = google-beta
  project  = var.project_id
  service  = "iap.googleapis.com"
}

# 1. ADK Agent Service
resource "google_cloud_run_v2_service" "agent" {
  name     = "rag-agent-${var.env}"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    timeout = "300s" # 5-minute timeout for cold starts
    
    # Enable CPU boost for faster startup
    # Note: Requires google-beta provider or specific resource version
    # Switching to standard annotations if startup_cpu_boost is not yet in GA for v2
    
    containers {
      image = var.agent_image
      
      resources {
        limits = {
          cpu    = "2"
          memory = "4096Mi"
        }
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.location
      }
      env {
        name  = "DATA_STORE_ID"
        value = var.data_store_id
      }
      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "false"
      }
      env {
        name = "GOOGLE_API_KEY"
        value_source {
          secret_key_ref {
            secret  = var.gemini_api_key_secret_name
            version = "latest"
          }
        }
      }
    }
  }
}

# 2. React UI Service
resource "google_cloud_run_v2_service" "ui" {
  name     = "rag-ui-${var.env}"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    containers {
      image = var.ui_image
    }
  }
}

# 3. Serverless NEGs for the Load Balancer
resource "google_compute_region_network_endpoint_group" "agent_neg" {
  name                  = "agent-neg-${var.env}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  cloud_run {
    service = google_cloud_run_v2_service.agent.name
  }
}

resource "google_compute_region_network_endpoint_group" "ui_neg" {
  name                  = "ui-neg-${var.env}"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  project               = var.project_id
  cloud_run {
    service = google_cloud_run_v2_service.ui.name
  }
}

# 4. IAM - Allow Invocation
resource "google_cloud_run_v2_service_iam_member" "agent_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.agent.name
  role     = "roles/run.invoker"
  member   = "user:${var.user_email}"
}

resource "google_cloud_run_v2_service_iam_member" "ui_invoker" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.ui.name
  role     = "roles/run.invoker"
  member   = "user:${var.user_email}"
}

# 4a. IAM - Allow IAP to invoke Cloud Run
resource "google_cloud_run_v2_service_iam_member" "iap_invoker_agent" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.agent.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_project_service_identity.iap_identity.email}"
}

resource "google_cloud_run_v2_service_iam_member" "iap_invoker_ui" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.ui.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_project_service_identity.iap_identity.email}"
}

# 5. IAP Permissions - Allow through proxy
resource "google_project_iam_member" "iap_accessor" {
  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "user:${var.user_email}"
}

output "agent_neg_id" { value = google_compute_region_network_endpoint_group.agent_neg.id }
output "ui_neg_id" { value = google_compute_region_network_endpoint_group.ui_neg.id }
