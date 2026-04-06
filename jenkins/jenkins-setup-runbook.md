# Jenkins Setup Runbook (End-to-End CI/CD + IaC)

## 1. Required Jenkins Credentials

Create these credentials in Jenkins before running the pipeline:

1. `docker-registry-creds` (Username/Password)
- Username: AWS Access Key ID with ECR push permissions (or Docker registry username)
- Password: AWS Secret Access Key (or Docker registry password/token)

2. `banking-aws-creds` (AWS Credentials)
- Type: AWS Credentials
- Credential ID: must match `AWS_CREDENTIALS_ID`
- Scope: Global

## 2. Jenkins Job Environment Variables

Use values from [jenkins/job-vars.example.env](jenkins/job-vars.example.env).

Minimum required for full automation:
- `DOCKER_REGISTRY`
- `AWS_REGION`
- `EKS_CLUSTER_NAME`
- `AWS_CREDENTIALS_ID`
- `TERRAFORM_ENABLED`
- `TERRAFORM_AUTO_APPLY`

## 3. IAM Permissions Needed

Ensure Jenkins AWS principal can:
- ECR: push/pull images
- EKS: describe cluster, update kubeconfig, interact with cluster auth
- EC2/VPC/IAM resources used by Terraform EKS module
- Optional: Route53/ACM if your ingress/TLS flow requires it

## 4. Recommended First Run Mode

For safer first execution:
- `TERRAFORM_ENABLED=true`
- `TERRAFORM_AUTO_APPLY=false`

This gives plan + build + scans without mutating infrastructure.

Then switch to full mode:
- `TERRAFORM_AUTO_APPLY=true`

## 5. One-Run Execution Checklist

1. Trigger Jenkins pipeline on `main`.
2. Confirm Terraform stages complete (fmt/validate/plan/apply if enabled).
3. Confirm image build and Trivy scan pass.
4. Confirm image push succeeds.
5. Confirm K8s deployment rollout status succeeds.
6. Confirm post-deploy smoke checks list running pods/service/ingress.

## 6. Quick Verification Commands

After successful run:

```bash
kubectl -n banking get deploy,pods,svc,ingress
```

## 7. Troubleshooting Pointers

- ECR push fails: verify `DOCKER_REGISTRY` format and `docker-registry-creds`.
- EKS deploy fails: verify `AWS_CREDENTIALS_ID`, `AWS_REGION`, and cluster name.
- Terraform apply fails: run local `terraform plan` in [terraform/aws](terraform/aws).
