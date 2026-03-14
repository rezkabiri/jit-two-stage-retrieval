# infrastructure/modules/monitoring/main.tf

variable "project_id" { type = string }
variable "env" { type = string }

resource "google_monitoring_dashboard" "rag_dashboard" {
  project        = var.project_id
  dashboard_json = jsonencode({
    displayName = "JIT RAG System Health (${var.env})"
    gridLayout = {
      columns = "2"
      widgets = [
        {
          title = "Cloud Run Request Count (Agent & UI)"
          xyChart = {
            dataSets = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\""
                    aggregation = { perSeriesAligner = "ALIGN_RATE" }
                  }
                }
                plotType = "LINE"
              }
            ]
          }
        },
        {
          title = "Cloud Run Latency (p95)"
          xyChart = {
            dataSets = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_latencies\""
                    aggregation = { 
                      perSeriesAligner = "ALIGN_PERCENTILE_95"
                      alignmentPeriod  = "60s" 
                    }
                  }
                }
                plotType = "LINE"
              }
            ]
          }
        },
        {
          title = "Error Rates (4xx & 5xx)"
          xyChart = {
            dataSets = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\" AND (metric.labels.response_code_class=\"4xx\" OR metric.labels.response_code_class=\"5xx\")"
                    aggregation = { perSeriesAligner = "ALIGN_RATE" }
                  }
                }
                plotType = "BAR"
              }
            ]
          }
        },
        {
          title = "BigQuery Feedback Ingestion (Rows)"
          xyChart = {
            dataSets = [
              {
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "resource.type=\"bigquery_dataset\" AND metric.type=\"bigquery.googleapis.com/storage/uploaded_row_count\""
                    aggregation = { perSeriesAligner = "ALIGN_DELTA" }
                  }
                }
                plotType = "LINE"
              }
            ]
          }
        }
      ]
    }
  })
}
