#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${IMAGE:-}" ]]; then
  echo "IMAGE environment variable is required, for example: docker.io/org/mobile-banking-backend:1"
  exit 1
fi

MINIKUBE_PROFILE="${MINIKUBE_PROFILE:-minikube}"

minikube -p "${MINIKUBE_PROFILE}" status
kubectl config use-context "${MINIKUBE_PROFILE}" || true
minikube -p "${MINIKUBE_PROFILE}" image load "${IMAGE}"
kubectl version --request-timeout=15s
kubectl apply --validate=false --request-timeout=15s -f k8s/namespace.yaml
sed "s|REPLACE_WITH_IMAGE|${IMAGE}|g" k8s/deployment.yaml | kubectl apply --validate=false --request-timeout=15s -f -
kubectl apply --validate=false --request-timeout=15s -f k8s/service.yaml
kubectl -n banking rollout status deployment/banking-backend --timeout=120s
kubectl -n banking get pods,svc
minikube -p "${MINIKUBE_PROFILE}" service banking-backend-service -n banking --url

echo "Deployment completed successfully"
