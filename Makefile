# JIT Two-Stage Retrieval Agentic RAG - Makefile

.PHONY: install setup-dev-env playground test eval deploy-stage deploy-prod manual-ingestion-stage

install:
	@echo "Installing dependencies..."
	pip install -r app/requirements.txt -r data-pipeline/ingestion/requirements.txt

setup-dev-env:
	@echo "Setting up infrastructure via Terraform..."
	cd infrastructure/environments/stage && terraform apply

playground:
	@echo "Starting ADK playground..."
	# adk web .

test:
	@echo "Running unit and integration tests..."
	export PYTHONPATH=$PYTHONPATH:$(pwd) && pytest app/tests/ data-pipeline/tests/

eval:
	@echo "Running ADK quality evaluation..."
	# adk eval app eval/eval_cases.json

deploy-stage:
	@echo "Deploying to Staging via Cloud Build..."
	gcloud builds submit --config cicd/cloudbuild.yaml --substitutions=_STAGING_PROJECT_ID=jit-tsr-rag-stage

deploy-prod:
	@echo "Deploying to Production via Cloud Build..."
	gcloud builds submit --config cicd/cloudbuild.yaml --substitutions=_STAGING_PROJECT_ID=jit-tsr-rag-stage,_PROD_PROJECT_ID=jit-tsr-rag-prod

manual-ingestion-stage:
	@echo "Manually deploying ingestion function to staging (break glass)..."
	./scripts/bootstrap/manual_deploy_ingestion.sh jit-tsr-rag-stage stage rag-docs-stage-d8ebf82b
