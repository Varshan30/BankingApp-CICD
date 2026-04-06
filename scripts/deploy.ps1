$ErrorActionPreference = "Stop"

if (-not $env:IMAGE -or [string]::IsNullOrWhiteSpace($env:IMAGE)) {
  Write-Error "IMAGE environment variable is required, for example: docker.io/org/mobile-banking-backend:1"
}

$minikubeProfile = if ($env:MINIKUBE_PROFILE) { $env:MINIKUBE_PROFILE } else { "minikube" }

minikube -p $minikubeProfile status
kubectl config use-context $minikubeProfile | Out-Null
minikube -p $minikubeProfile image load $env:IMAGE
kubectl version --request-timeout=15s
kubectl apply --validate=false --request-timeout=15s -f k8s/namespace.yaml
(Get-Content k8s/deployment.yaml -Raw).Replace("REPLACE_WITH_IMAGE", $env:IMAGE) | kubectl apply --validate=false --request-timeout=15s -f -
kubectl apply --validate=false --request-timeout=15s -f k8s/service.yaml
kubectl -n banking rollout status deployment/banking-backend --timeout=120s
kubectl -n banking get pods,svc
minikube -p $minikubeProfile service banking-backend-service -n banking --url

Write-Output "Deployment completed successfully"
