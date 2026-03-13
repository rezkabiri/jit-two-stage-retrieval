# infrastructure/modules/storage/main.tf: Storage for RAG Ingestion

variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "env" {
  type = string
}

resource "google_storage_bucket" "ingestion_bucket" {
  project       = var.project_id
  name          = "${var.project_id}-${var.env}-ingestion"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
}

resource "google_storage_bucket" "feedback_bucket" {
  project       = var.project_id
  name          = "${var.project_id}-${var.env}-feedback"
  location      = var.region
  force_destroy = true
  
  uniform_bucket_level_access = true
}

output "ingestion_bucket_name" {
  value = google_storage_bucket.ingestion_bucket.name
}
