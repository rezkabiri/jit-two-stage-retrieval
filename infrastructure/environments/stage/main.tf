# infrastructure/environments/stage/main.tf: Staging Environment Deployment

terraform {
  required_version = ">= 1.5.0"
  backend "gcs" {}
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

provider "google" {
  project                 = var.project_id
  region                  = var.region
  user_project_override   = true
  billing_project         = var.project_id
}

module "project" {
  source     = "../../modules/project"
  project_id = var.project_id
}

module "storage" {
  source     = "../../modules/storage"
  project_id = module.project.project_id
  region     = var.region
  env        = "stage"
}

module "vertex_ai" {
  source     = "../../modules/vertex_ai"
  project_id = module.project.project_id
  region     = var.region
  env        = "stage"
}

module "secrets" {
  source                = "../../modules/secrets"
  project_id            = module.project.project_id
  env                   = "stage"
  gemini_api_key        = var.gemini_api_key
  service_account_email = "${module.project.project_number}-compute@developer.gserviceaccount.com"
}

module "cloud_run" {
  source                     = "../../modules/cloud_run"
  project_id                 = module.project.project_id
  region                     = var.region
  env                        = "stage"
  agent_image                = var.agent_image
  ui_image                   = var.ui_image
  data_store_id              = module.vertex_ai.data_store_id
  gemini_api_key_secret_name = module.secrets.secret_id
  user_email                 = var.user_email
}

module "load_balancer" {
  source            = "../../modules/load_balancer"
  project_id        = module.project.project_id
  env               = "stage"
  agent_neg_id      = module.cloud_run.agent_neg_id
  ui_neg_id         = module.cloud_run.ui_neg_id
  iap_client_id     = var.iap_client_id
  iap_client_secret = var.iap_client_secret
  user_email        = var.user_email
}

module "monitoring" {
  source     = "../../modules/monitoring"
  project_id = module.project.project_id
  env        = "stage"
}

module "ingestion" {
  source                = "../../modules/ingestion"
  project_id            = module.project.project_id
  region                = var.region
  env                   = "stage"
  ingestion_bucket_name = module.storage.ingestion_bucket_name
  data_store_id         = module.vertex_ai.data_store_id
}

output "project_id" { value = module.project.project_id }
output "ingestion_bucket" { value = module.storage.ingestion_bucket_name }
output "load_balancer_ip" { value = module.load_balancer.load_balancer_ip }
