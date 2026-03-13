# JIT Two-Stage Retrieval Agentic RAG - Makefile

.PHONY: install setup-dev-env playground test eval deploy-stage deploy-prod

install:
	@echo "Installing dependencies..."
	# uv sync (or pip install -r requirements.txt)

setup-dev-env:
	@echo "Setting up infrastructure via Terraform..."
	# cd infrastructure/environments/stage && terraform apply

playground:
	@echo "Starting ADK playground..."
	# adk web .

test:
	@echo "Running unit and integration tests..."
	pytest app/tests frontend/tests data-pipeline/tests

eval:
	@echo "Running ADK quality evaluation..."
	# adk eval app eval/eval_cases.json

deploy-stage:
	@echo "Deploying to Staging..."
	# gcloud builds submit --config cicd/cloudbuild.yaml --substitutions=_ENV=stage

deploy-prod:
	@echo "Deploying to Production..."
	# gcloud builds submit --config cicd/cloudbuild.yaml --substitutions=_ENV=prod
