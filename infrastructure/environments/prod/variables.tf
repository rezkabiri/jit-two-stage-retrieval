# infrastructure/environments/prod/variables.tf: Environment-specific variables

variable "project_id" {
  description = "The existing GCP Project ID for production"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

variable "agent_image" { 
  type    = string
  default = "gcr.io/cloudrun/hello" # Placeholder
}

variable "ui_image" { 
  type    = string
  default = "gcr.io/cloudrun/hello" # Placeholder
}

variable "user_email" {
  type        = string
  description = "Your Google Cloud email for invoker permissions"
}

variable "iap_client_id" { 
  type    = string
  default = "placeholder-id"
}

variable "iap_client_secret" { 
  type    = string
  default = "placeholder-secret"
}

variable "gemini_api_key" {
  type        = string
  description = "The API key for Gemini (AI Studio)"
  sensitive   = true
}
