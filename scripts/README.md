# Utility & Operational Scripts

This directory contains scripts for environment setup, maintenance, and security validation.

## Directory Structure

- **bootstrap/**: Cold-start scripts for initializing GCP projects and Terraform state.
- **dr/**: Disaster Recovery and Data Store rebuild drills.
- **local-dev/**: Scripts to setup and run the application on a local machine.
- **red-team/**: Security simulation scripts to verify RBAC and data isolation.

## Key Scripts

### Disaster Recovery
- `scripts/dr/rebuild_datastore.sh`: Automates the deletion and full re-ingestion of the Search index.

### Security (Red Team)
- `scripts/red-team/simulate_security_breach.py`: Proactively tests for data leakage by simulating unauthorized queries.

### Bootstrap
- `scripts/bootstrap/bootstrap.sh`: Initializes GCP APIs and project infrastructure.
