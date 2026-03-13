# infrastructure/environments/prod/main.tf: Production Environment Deployment

terraform {
  required_version = ">= 1.5.0"
  backend "gcs" {}
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 7.0"
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
  env        = "prod"
}

module "vertex_ai" {
  source     = "../../modules/vertex_ai"
  project_id = module.project.project_id
  region     = var.region
}

module "cloud_run" {
  source        = "../../modules/cloud_run"
  project_id    = module.project.project_id
  region        = var.region
  env           = "prod"
  agent_image   = var.agent_image
  ui_image      = var.ui_image
  data_store_id = module.vertex_ai.data_store_id
}

module "load_balancer" {
  source            = "../../modules/load_balancer"
  project_id        = module.project.project_id
  env               = "prod"
  agent_neg_id      = module.cloud_run.agent_neg_id
  ui_neg_id         = module.cloud_run.ui_neg_id
  iap_client_id     = var.iap_client_id
  iap_client_secret = var.iap_client_secret
}

module "monitoring" {
  source     = "../../modules/monitoring"
  project_id = module.project.project_id
  env        = "prod"
}

output "project_id" { value = module.project.project_id }
output "ingestion_bucket" { value = module.storage.ingestion_bucket_name }
