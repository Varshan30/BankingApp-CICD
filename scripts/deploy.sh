#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${IMAGE:-}" ]]; then
  echo "IMAGE environment variable is required, for example: docker.io/org/mobile-banking-backend:1"
  exit 1
fi

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/cert-issuer.yaml
sed "s|REPLACE_WITH_IMAGE|${IMAGE}|g" k8s/deployment.yaml | kubectl apply -f -
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/networkpolicy.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml
kubectl -n banking rollout status deployment/banking-backend --timeout=120s

echo "Deployment completed successfully"
