#!/usr/bin/env bash
set -euo pipefail

pushd terraform/aws > /dev/null
terraform init
terraform plan -out tfplan
terraform apply tfplan
popd > /dev/null

echo "Infrastructure provisioned."
echo "Next: configure kubectl with AWS CLI and deploy the app."
echo "aws eks update-kubeconfig --name <eks_cluster_name> --region <aws_region>"
