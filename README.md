# DevOps CI/CD Pipeline for Mobile Banking Backend

This repository is a complete starter implementation for an automated CI/CD system designed for a mobile banking backend.

It demonstrates:

- Continuous Integration with automated tests
- Security gates (SAST, dependency scan, container image scan)
- Container image build and push
- Automated infrastructure provisioning with Terraform modules (optional, AWS)
- Continuous Deployment to Minikube with rolling updates
- Production hardening with ingress TLS, autoscaling, and network policies

## Repository Structure

- `app/` - Sample Flask backend and unit tests
- `Dockerfile` - Container build definition
- `k8s/` - Kubernetes manifests (deployment, service, ingress, TLS, HPA, network policies)
- `terraform/aws/` - Terraform modules for VPC + EKS + ECR
- `Jenkinsfile` - End-to-end CI/CD pipeline
- `scripts/` - Helper scripts for infra bootstrap, deployment, and ingress/TLS

## Architecture Summary

### Toolchain

- Source Control: GitHub/GitLab
- CI/CD: Jenkins
- Containerization: Docker
- Orchestration: Minikube (local Kubernetes)
- Infrastructure as Code: Terraform modules (VPC + EKS) for optional AWS environments

### End-to-End Flow

1. Developers push backend code.
2. Jenkins pipeline triggers automatically.
3. Security gates run (Bandit, pip-audit, Trivy).
4. Docker image is built.
5. Docker image is loaded into Minikube.
6. Application is deployed to Minikube using rolling update strategy.
6. Ingress, TLS, HPA, and network policies are enforced.

### Reliability Features

- Rolling deployments with max surge/unavailable settings
- Liveness and readiness probes
- Multi-replica deployment
- Horizontal pod autoscaling
- Namespace-level network controls
- Idempotent infrastructure automation with Terraform modules

### Security Considerations

- Keep secrets in Jenkins credentials or secret manager
- Restrict EKS API endpoint access CIDRs in Terraform
- Use image scanning before deployment
- Enforce TLS ingress and network policies in production

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

## 3) (Optional) Provision AWS infrastructure with Terraform

```bash
cd terraform/aws
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars
terraform init
terraform apply
```

## 4) Start Minikube and set kubectl context

```bash
minikube start
kubectl config use-context minikube
```

## 5) Enable Minikube ingress

```bash
minikube addons enable ingress
```

## 6) Deploy to Minikube

```bash
export IMAGE=mobile-banking-backend:local
./scripts/deploy.sh
```

PowerShell (Windows):

```powershell
$env:IMAGE="mobile-banking-backend:local"
./scripts/deploy.ps1
```

## 7) Configure Jenkins Pipeline

Create a Pipeline job that points to this repository and uses the root `Jenkinsfile`.

Set job environment variables:

- `DOCKER_REGISTRY`
- `DEPLOY_TARGET` (`minikube`)
- `MINIKUBE_PROFILE` (default `minikube`)
- `INGRESS_MANIFEST` (default `k8s/ingress.minikube.yaml`)
- `APPLY_INGRESS` (`true`/`false`, default `false`)
- `ANSIBLE_ENABLED` (`true`/`false`, optional)
- `ANSIBLE_PLAYBOOK` (optional, default `ansible/playbooks/site.yml`)
- `ANSIBLE_INVENTORY` (optional, default `ansible/inventory/hosts.ini`)

Create Jenkins credentials (optional, only when pushing to a remote registry):

- `docker-registry-creds` (username/password)

Pipeline security gates:

- Bandit for SAST
- pip-audit for Python dependency vulnerabilities
- Trivy for container image vulnerabilities

Pipeline integration flow (Jenkins):

- Resolve image reference
- Optional Ansible bootstrap run
- Unit tests + SAST + dependency scan
- Docker build + Trivy scan
- Optional push image to remote registry (non-minikube targets)
- Minikube preflight check
- Load image into Minikube
- Kubernetes manifest validation
- Deploy to Minikube (main/master)
- Post-deploy smoke checks

Ingress is optional by default for Minikube (`APPLY_INGRESS=false`).
Use service URL or port-forward for local access; enable ingress only when nginx admission is ready.

## 8) GitHub Actions CI/CD

This repository now includes GitHub Actions workflow at `.github/workflows/ci-cd.yml`.

Workflow behavior:

- Runs on every pull request to `main`
- Runs on every push to `main`
- Executes unit tests, Bandit SAST, and pip-audit dependency checks
- Builds Docker image in the runner and scans it with Trivy
- On push to `main`, authenticates to AWS, pushes image to ECR, and deploys to EKS

Required GitHub repository secrets:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

Recommended GitHub repository variables:

- `AWS_REGION` (default in workflow: `ap-south-1`)
- `EKS_CLUSTER_NAME` (default in workflow: `banking-devops-eks`)
- `ECR_REPOSITORY` (default in workflow: `banking-devops/mobile-banking-backend`)

The Jenkins pipeline remains available as an alternative for teams that prefer Jenkins-based orchestration.

## Mapping to Your Project Plan

- Phase 1: Requirements captured in this design and toolchain
- Phase 2: `terraform/aws/` provisions VPC, EKS, and ECR with Terraform modules
- Phase 3: Managed cluster operations are handled by EKS control plane
- Phase 4: `Dockerfile` containerizes backend service
- Phase 5: `Jenkinsfile` implements CI/CD automation and security quality gates
- Phase 6: `k8s/` deploys rolling, hardened workloads with ingress/TLS/autoscaling

## Production Hardening Suggestions

- Enable AWS WAF in front of ingress for API protection
- Add Open Policy Agent or Kyverno admission controls
- Integrate secrets manager (Vault/AWS Secrets Manager)
- Add PodDisruptionBudgets and topology spread constraints
- Add canary or blue-green deployment strategy
