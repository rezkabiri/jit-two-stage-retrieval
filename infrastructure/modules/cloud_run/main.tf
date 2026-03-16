# infrastructure/modules/cloud_run/main.tf

variable "project_id" { type = string }
variable "region" { type = string }
variable "env" { type = string }
variable "agent_image" { type = string }
variable "ui_image" { type = string }
variable "data_store_id" { type = string }
variable "user_email" { 
  type        = string
  description = "The email address of the user allowed to invoke the services"
}

# 1. ADK Agent Service
resource "google_cloud_run_v2_service" "agent" {
  name     = "rag-agent-${var.env}"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_INTERNAL_AND_CLOUD_LOAD_BALANCING"

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
        value = var.region
      }
      env {
        name  = "DATA_STORE_ID"
        value = var.data_store_id
      }
    }
  }
}

# 2. React UI Service
resource "google_cloud_run_v2_service" "ui" {
  name     = "rag-ui-${var.env}"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_INTERNAL_AND_CLOUD_LOAD_BALANCING"

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

# 5. IAP Permissions - Allow through proxy
resource "google_project_iam_member" "iap_accessor" {
  project = var.project_id
  role    = "roles/iap.httpsResourceAccessor"
  member  = "user:${var.user_email}"
}

output "agent_neg_id" { value = google_compute_region_network_endpoint_group.agent_neg.id }
output "ui_neg_id" { value = google_compute_region_network_endpoint_group.ui_neg.id }
