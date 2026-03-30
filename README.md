# DevOps CI/CD Pipeline for Mobile Banking Backend

This repository is a complete starter implementation for an automated CI/CD system designed for a mobile banking backend.

It demonstrates:

- Continuous Integration with automated tests
- Security gates (SAST, dependency scan, container image scan)
- Container image build and push
- Automated infrastructure provisioning with Terraform modules
- Continuous Deployment to Amazon EKS with rolling updates
- Production hardening with ingress TLS, autoscaling, and network policies
- Monitoring and alerting with Prometheus, Grafana, and Alertmanager
- Centralized logging with Loki and Promtail

## Repository Structure

- `app/` - Sample Flask backend and unit tests
- `Dockerfile` - Container build definition
- `k8s/` - Kubernetes manifests (deployment, service, ingress, TLS, HPA, network policies)
- `terraform/aws/` - Terraform modules for VPC + EKS + ECR
- `monitoring/` - Helm values for Prometheus/Grafana/Alertmanager and Loki
- `Jenkinsfile` - End-to-end CI/CD pipeline
- `scripts/` - Helper scripts for infra bootstrap, deployment, ingress/TLS, and observability install
- `docs/` - Architecture notes

## Quick Start

## 1) Run the app locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
python app/app.py
```

The service starts on port `8080`.

## 2) Build Docker image

```bash
docker build -t mobile-banking-backend:local .
```

## 3) Provision infrastructure with Terraform

```bash
cd terraform/aws
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform apply
```

## 4) Configure kubectl for EKS

```bash
aws eks update-kubeconfig --name <eks_cluster_name> --region <aws_region>
```

## 5) Install ingress and cert-manager

```bash
./scripts/install_ingress_tls.sh
```

## 6) Deploy to EKS

```bash
export IMAGE=docker.io/your-org/mobile-banking-backend:1
./scripts/deploy.sh
```

## 7) Install monitoring and centralized logging

```bash
./scripts/install_observability.sh
```

## 8) Configure Jenkins Pipeline

Create a Pipeline job that points to this repository and uses the root `Jenkinsfile`.

Set job environment variables:

- `DOCKER_REGISTRY`
- `AWS_CREDENTIALS_ID`
- `AWS_REGION`
- `EKS_CLUSTER_NAME`
- `DEPLOY_OBSERVABILITY`

Create Jenkins credentials:

- `docker-registry-creds` (username/password)
- AWS credentials referenced by `AWS_CREDENTIALS_ID`

Pipeline security gates:

- Bandit for SAST
- pip-audit for Python dependency vulnerabilities
- Trivy for container image vulnerabilities

## Mapping to Your Project Plan

- Phase 1: Requirements captured in this design and toolchain
- Phase 2: `terraform/aws/` provisions VPC, EKS, and ECR with Terraform modules
- Phase 3: Managed cluster operations are handled by EKS control plane
- Phase 4: `Dockerfile` containerizes backend service
- Phase 5: `Jenkinsfile` implements CI/CD automation and security quality gates
- Phase 6: `k8s/` deploys rolling, hardened workloads with ingress/TLS/autoscaling
- Phase 7: `monitoring/` and scripts provide monitoring, alerting, and centralized logging

## Production Hardening Suggestions

- Enable AWS WAF in front of ingress for API protection
- Add Open Policy Agent or Kyverno admission controls
- Integrate secrets manager (Vault/AWS Secrets Manager)
- Add PodDisruptionBudgets and topology spread constraints
- Add canary or blue-green deployment strategy
