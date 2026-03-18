# infrastructure/modules/ingestion/variables.tf

variable "project_id" {
  type        = string
  description = "The GCP Project ID"
}

variable "region" {
  type        = string
  description = "The region to deploy to"
}

variable "env" {
  type        = string
  description = "The environment (stage, prod)"
}

variable "ingestion_bucket_name" {
  type        = string
  description = "The name of the GCS bucket for ingestion"
}

variable "data_store_id" {
  type        = string
  description = "The Vertex AI Search Data Store ID"
}
