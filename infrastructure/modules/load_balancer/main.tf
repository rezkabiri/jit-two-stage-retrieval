# infrastructure/modules/load_balancer/main.tf

variable "project_id" { type = string }
variable "env" { type = string }
variable "agent_neg_id" { type = string }
variable "ui_neg_id" { type = string }
variable "iap_client_id" { type = string }
variable "iap_client_secret" { type = string }
variable "user_email" { type = string }

# 0. Reserve Static IP
resource "google_compute_global_address" "default" {
  name    = "rag-lb-ip-${var.env}"
  project = var.project_id
}

# 1. URL Map (Routing Logic)
resource "google_compute_url_map" "default" {
  name            = "rag-lb-${var.env}"
  project         = var.project_id
  default_service = google_compute_backend_service.ui.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.ui.id

    path_rule {
      paths   = ["/api/*"]
      service = google_compute_backend_service.agent.id
    }
  }
}

# 2. Backend Service for Agent (IAP Enabled)
resource "google_compute_backend_service" "agent" {
  name                  = "agent-backend-${var.env}"
  project               = var.project_id
  load_balancing_scheme = "EXTERNAL_MANAGED"

  backend {
    group = var.agent_neg_id
  }

  iap {
    enabled              = true
    oauth2_client_id     = var.iap_client_id
    oauth2_client_secret = var.iap_client_secret
  }
}

# 3. Backend Service for UI (IAP Enabled)
resource "google_compute_backend_service" "ui" {
  name                  = "ui-backend-${var.env}"
  project               = var.project_id
  load_balancing_scheme = "EXTERNAL_MANAGED"

  backend {
    group = var.ui_neg_id
  }

  iap {
    enabled              = true
    oauth2_client_id     = var.iap_client_id
    oauth2_client_secret = var.iap_client_secret
  }
}

# 4. IAM for IAP - Grant access to the backends
resource "google_compute_iap_web_backend_service_iam_member" "agent_accessor" {
  project            = var.project_id
  web_backend_service = google_compute_backend_service.agent.name
  role               = "roles/iap.httpsResourceAccessor"
  member             = "user:${var.user_email}"
}

resource "google_compute_iap_web_backend_service_iam_member" "ui_accessor" {
  project            = var.project_id
  web_backend_service = google_compute_backend_service.ui.name
  role               = "roles/iap.httpsResourceAccessor"
  member             = "user:${var.user_email}"
}

# 5. SSL Certificate (Self-signed for testing)
resource "google_compute_managed_ssl_certificate" "default" {
  name    = "rag-cert-${var.env}"
  project = var.project_id
  managed {
    domains = ["rag-${var.env}.example.com"] # Replace with your real domain later
  }
}

# 6. Global Forwarding Rule (HTTPS)
resource "google_compute_global_forwarding_rule" "default" {
  name                  = "rag-forwarding-rule-${var.env}"
  project               = var.project_id
  load_balancing_scheme = "EXTERNAL_MANAGED"
  target                = google_compute_target_https_proxy.default.id
  port_range            = "443"
  ip_address            = google_compute_global_address.default.address
}

resource "google_compute_target_https_proxy" "default" {
  name             = "rag-https-proxy-${var.env}"
  project          = var.project_id
  url_map          = google_compute_url_map.default.id
  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}
