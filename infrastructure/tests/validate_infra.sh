#!/bin/bash
# infrastructure/tests/validate_infra.sh: Validation script for IaC

set -e

echo "🔍 Running Infrastructure Validation Tests..."

# 1. Terraform Format Check
echo "Step 1: Checking Terraform formatting..."
terraform fmt -recursive -check

# 2. Terraform Validation
for env in "stage" "prod"; do
    echo "Step 2: Validating Terraform configuration for '$env' environment..."
    cd "infrastructure/environments/$env"
    terraform init -backend=false
    terraform validate
    cd - > /dev/null
done

# 3. TFLint (Optional, if installed)
if command -v tflint >/dev/null 2>&1; then
    echo "Step 3: Running TFLint..."
    tflint --init
    tflint --recursive
else
    echo "Step 3: skipping TFLint (not installed)."
fi

echo "✅ Infrastructure validation passed!"
