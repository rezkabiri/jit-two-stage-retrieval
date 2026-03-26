# Monitoring & Observability

This document provides a deep dive into the monitoring strategy for the JIT Two-Stage Retrieval RAG system.

## Overview

A production-grade RAG system requires high visibility into its three core components: **Retrieval Latency**, **Model Performance**, and **Data Integrity**. We use **Google Cloud Monitoring** to provide a unified health dashboard, provisioned automatically via Terraform.

---

## The "JIT RAG System Health" Dashboard

The dashboard is designed for "at-a-glance" verification of the system's operational status. It is located in the Google Cloud Console under **Monitoring > Dashboards**.

### 1. Cloud Run Performance (Agent & UI)
- **Request Count**: Monitors the total throughput of the system. Sudden drops may indicate DNS or Load Balancer issues.
- **Latency (p95)**: Tracks the 95th percentile response time. For a two-stage RAG, this is the most critical metric. High latency usually indicates a bottleneck in either the Vertex AI Search (Stage 1) or the Reranking/Generation (Stage 2) turns.
- **Error Rates (4xx & 5xx)**: Visualizes failed requests. 
    - **4xx errors** often point to authentication (IAP) issues or RBAC rejections.
    - **5xx errors** indicate code crashes or upstream API timeouts (Vertex AI).

### 2. Feedback & Data Pipeline
- **BigQuery Feedback Ingestion**: Tracks the rate of rows being written to the `user_feedback` table. This ensures the "Continuous Improvement" loop is functional. If users are clicking 👍/👎 but this graph is flat, there is an issue with the background task or BigQuery permissions.

---

## Infrastructure as Code (IaC)

The dashboard is defined in `infrastructure/modules/monitoring/main.tf`. This ensures that:
1. **Consistency**: Every environment (Stage, Prod) has the exact same monitoring view.
2. **Version Control**: Changes to the monitoring strategy (e.g., adding a new widget for Vertex AI token usage) are reviewed and committed just like application code.

---

## Troubleshooting with Metrics

| Symptom | Metric to Check | Likely Root Cause |
| :--- | :--- | :--- |
| **"I'm not getting answers."** | Error Rates (4xx) | IAP identity not passed or RBAC filter returning 0 results. |
| **"The agent is very slow."** | Latency (p95) | Large document snippets in Stage 1 or high `top_k` in Reranker. |
| **"Feedback isn't appearing."** | BQ Ingestion | Cloud Run Service Account missing `roles/bigquery.dataEditor`. |
| **"The UI is blank."** | Request Count | Load Balancer Global IP or SSL certificate issue. |

---

## Future Roadmap

- **Log-Based Alerts**: Automatically notify Slack/Email when the agent logs a `hallucination_detected` event.
- **Vertex AI Quota Monitoring**: Dashboard widgets to track Gemini API and Ranking API quota usage to prevent `429` errors.
- **Trace Integration**: Linking dashboard spikes directly to **Cloud Trace** for deep-dive request analysis.
