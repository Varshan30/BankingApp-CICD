#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${IMAGE:-}" ]]; then
  echo "IMAGE environment variable is required, for example: docker.io/org/mobile-banking-backend:1"
  exit 1
fi

MINIKUBE_PROFILE="${MINIKUBE_PROFILE:-minikube}"
INGRESS_MANIFEST="${INGRESS_MANIFEST:-k8s/ingress.minikube.yaml}"
APPLY_INGRESS="${APPLY_INGRESS:-false}"

minikube -p "${MINIKUBE_PROFILE}" status
kubectl config use-context "${MINIKUBE_PROFILE}" || true
minikube -p "${MINIKUBE_PROFILE}" addons enable ingress
minikube -p "${MINIKUBE_PROFILE}" addons enable metrics-server || true
minikube -p "${MINIKUBE_PROFILE}" image load "${IMAGE}"
kubectl version --request-timeout=15s
kubectl apply --validate=false --request-timeout=15s -f k8s/namespace.yaml
sed "s|REPLACE_WITH_IMAGE|${IMAGE}|g" k8s/deployment.yaml | kubectl apply --validate=false --request-timeout=15s -f -
kubectl apply --validate=false --request-timeout=15s -f k8s/service.yaml
kubectl apply --validate=false --request-timeout=15s -f k8s/networkpolicy.yaml
kubectl apply --validate=false --request-timeout=15s -f k8s/hpa.yaml
if [[ "${APPLY_INGRESS}" == "true" ]]; then
  kubectl apply --validate=false --request-timeout=15s -f "${INGRESS_MANIFEST}"
fi
kubectl -n banking rollout status deployment/banking-backend --timeout=120s
minikube -p "${MINIKUBE_PROFILE}" service banking-backend-service -n banking --url

echo "Deployment completed successfully"
