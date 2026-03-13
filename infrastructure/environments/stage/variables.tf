# infrastructure/environments/stage/variables.tf: Environment-specific variables

variable "project_id" {
  description = "The existing GCP Project ID for staging"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "agent_image" { type = string }
variable "ui_image" { type = string }
variable "iap_client_id" { type = string }
variable "iap_client_secret" { type = string }
