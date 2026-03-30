# Jenkins Configuration Notes

Create these Jenkins credentials before running the pipeline:

1. `docker-registry-creds` (Username/Password)
2. AWS credentials referenced by `AWS_CREDENTIALS_ID`

Recommended environment variables for the pipeline job:

- `DOCKER_REGISTRY` (e.g., `docker.io/your-org`)
- `AWS_CREDENTIALS_ID` (e.g., `banking-aws-creds`)
- `AWS_REGION` (e.g., `us-east-1`)
- `EKS_CLUSTER_NAME` (e.g., `banking-devops-eks`)
- `DEPLOY_OBSERVABILITY` (`true`/`false`)

Security gates enabled in the pipeline:

- SAST with Bandit
- Dependency scanning with pip-audit
- Container image scanning with Trivy
