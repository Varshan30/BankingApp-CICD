# Mobile Banking Backend (Simple Setup)

This project is now set up with simple, easy-to-learn tools first.

Default stack:

- Flask app
- Docker and Docker Compose
- Jenkins for basic CI (test + build)
- Simple local run scripts

Advanced infrastructure folders are still present, but they are optional.

## Repository Structure

- `app/` - Flask backend and unit tests
- `Dockerfile` - Container build
- `docker-compose.yml` - One-command local container run
- `Jenkinsfile` - Simple CI pipeline (checkout, test, docker build)
- `scripts/run-local.ps1` - Local run script for Windows
- `scripts/run-local.sh` - Local run script for Linux/macOS
- `k8s/`, `terraform/` - Optional infrastructure

## Simple Development Flow

1. Run the app locally.
2. Run tests.
3. Build Docker image.
4. Optionally run with Docker Compose.
5. Let Jenkins run the same simple checks in CI.

## Quick Start

## 1) Run locally with Python (Windows)

```powershell
./scripts/run-local.ps1
```

## 2) Run locally with Python (Linux/macOS)

```bash
./scripts/run-local.sh
```

The service starts on port `8080`.

## 3) Run with Docker Compose

```bash
docker compose up --build
```

## 4) Run tests manually

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r app/requirements.txt
pytest app/test_app.py -q
```

## 5) Jenkins setup (simple)

Create a Pipeline job that uses the root `Jenkinsfile`.

What Jenkins does:

- Checkout code
- Create virtual environment
- Install dependencies
- Run unit tests
- Build Docker image

Only one Jenkins parameter is required:

- `APP_NAME` (default: `mobile-banking-backend`)

## 6) Optional advanced stack

If you want to learn advanced DevOps later, these are still available:

- Kubernetes manifests in `k8s/`
- Terraform modules in `terraform/aws/`

These are not required for the default project flow.

### Simple Minikube deploy (optional)

1. Start Minikube:

```bash
minikube start
```

2. Build image locally:

```bash
docker build -t mobile-banking-backend:local .
```

3. Deploy with script:

Linux/macOS:

```bash
export IMAGE=mobile-banking-backend:local
./scripts/deploy.sh
```

Windows PowerShell:

```powershell
$env:IMAGE="mobile-banking-backend:local"
./scripts/deploy.ps1
```

This simple Minikube flow only applies:

- `k8s/namespace.yaml`
- `k8s/deployment.yaml`
- `k8s/service.yaml`

## 7) Build Docker image directly

```bash
docker build -t mobile-banking-backend:local .
```

## 8) Terraform with EC2 + Minikube (Beginner)

Yes, you can use Terraform + EC2 + Minikube.

What Terraform creates now:

- ECR repository
- Optional EC2 host with Minikube installed (when `create_minikube_ec2=true`)

Steps:

1. Edit `terraform/aws/terraform.tfvars`:
	- set `create_minikube_ec2 = true`
	- set `ec2_size_profile = "small"` (or `"medium"`)
	- set `key_name` to your AWS key pair name
	- set `allowed_ssh_cidr` to your public IP with `/32`
	- keep `ec2_instance_type_override = ""` to stay on low-cost profile mode

2. Apply Terraform:

```bash
cd terraform/aws
terraform init
terraform apply
```

3. Get host details from outputs:

```bash
terraform output minikube_ec2_public_ip
terraform output minikube_ssh_command
```

Low-cost tips:

- Use `ec2_size_profile = "small"` for cheapest option.
- Stop the EC2 instance when not in use.
- Destroy resources after testing:

```bash
terraform destroy
```
