# Mobile Banking CI/CD Architecture

## Toolchain

- Source Control: GitHub/GitLab
- CI/CD: Jenkins
- Containerization: Docker
- Orchestration: Amazon EKS (managed Kubernetes)
- Infrastructure as Code: Terraform modules (VPC + EKS)

## End-to-End Flow

1. Developers push backend code.
2. Jenkins pipeline triggers automatically.
3. Security gates run (Bandit, pip-audit, Trivy).
4. Docker image is built and pushed to registry.
5. Application is deployed to EKS using rolling update strategy.
6. Ingress, TLS, HPA, and network policies are enforced.

## Reliability Features

- Rolling deployments with max surge/unavailable settings
- Liveness and readiness probes
- Multi-replica deployment
- Horizontal pod autoscaling
- Namespace-level network controls
- Idempotent infrastructure automation with Terraform modules

## Security Considerations

- Keep secrets in Jenkins credentials or secret manager
- Restrict EKS API endpoint access CIDRs in Terraform
- Use image scanning before deployment
- Enforce TLS ingress and network policies in production
