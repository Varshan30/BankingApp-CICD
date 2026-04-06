# Jenkins Configuration Notes

Create these Jenkins credentials before running the pipeline:

1. `docker-registry-creds` (Username/Password)
2. AWS credentials referenced by `AWS_CREDENTIALS_ID`

Recommended environment variables for the pipeline job:

- `DOCKER_REGISTRY` (e.g., `docker.io/your-org`)
- `AWS_CREDENTIALS_ID` (e.g., `banking-aws-creds`)
- `AWS_REGION` (e.g., `us-east-1`)
- `EKS_CLUSTER_NAME` (e.g., `banking-devops-eks`)
- `TERRAFORM_ENABLED` (`true`/`false`)
- `TERRAFORM_AUTO_APPLY` (`true`/`false`)
- `ANSIBLE_ENABLED` (`true`/`false`, optional)
- `ANSIBLE_PLAYBOOK` (optional, default `ansible/playbooks/site.yml`)
- `ANSIBLE_INVENTORY` (optional, default `ansible/inventory/hosts.ini`)

Security gates enabled in the pipeline:

- SAST with Bandit
- Dependency scanning with pip-audit
- Container image scanning with Trivy

Pipeline behavior notes:

- Unit test report is published from `reports/pytest.xml`
- Security and scan reports are archived from `reports/`
- Container push and EKS deploy stages run only for `main`/`master`
- Kubernetes manifests are validated with `kubectl --dry-run=client` before deployment
- Terraform outputs (`eks_cluster_name`, `ecr_repository_url`) are consumed when Terraform stages are enabled
- Optional Ansible bootstrap stage runs before application build/deploy when `ANSIBLE_ENABLED=true`
- Docker push authentication is selected automatically:
	- ECR registry (`*.amazonaws.com`): AWS credentials + `aws ecr get-login-password`
	- Other registries: `docker-registry-creds`

Ready-to-use setup artifacts:

- Environment variable template: `jenkins/job-vars.example.env`
- End-to-end setup checklist: `jenkins/jenkins-setup-runbook.md`
