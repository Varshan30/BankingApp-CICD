# Jenkins Setup Runbook (End-to-End CI/CD)

## 1. Required Jenkins Credentials

No credentials are required for the default simple pipeline.

## 2. Jenkins Job Environment Variables

Use values from [jenkins/job-vars.example.env](jenkins/job-vars.example.env).

Main pipeline controls are available as Jenkins job parameters:

- `APP_NAME`

## 3. Agent Tooling Requirements

Ensure Jenkins agent has:

- Docker daemon access
- Python 3 and pip

## 4. Recommended First Run Mode

For first execution:
- Keep `APP_NAME=mobile-banking-backend`.

This runs unit tests and Docker build only.

## 5. One-Run Execution Checklist

1. Trigger Jenkins pipeline on `main`.
2. Confirm unit tests pass.
3. Confirm image build succeeds.
4. Confirm `reports/pytest.xml` is archived in Jenkins build artifacts.

## 7. Troubleshooting Pointers

- Python setup fails: verify `python3` is available on Jenkins agent.
- Docker build fails: verify Docker daemon access from Jenkins agent user.

## 8. Optional Bootstrap with JCasC + Job DSL

Use repository artifacts:

- `jenkins/casc/jenkins.yaml`
- `jenkins/jobdsl/mobile-banking-backend.groovy`

Steps:

1. Install Jenkins plugins: Configuration as Code and Job DSL.
2. Set environment variable `CASC_JENKINS_CONFIG` to point at `jenkins/casc/jenkins.yaml`.
3. Set secure runtime variables before Jenkins start:
	- `JENKINS_ADMIN_USER`
	- `JENKINS_ADMIN_PASSWORD`
4. Restart Jenkins and confirm JCasC loads with no validation errors.
5. Edit repository URL in `jenkins/jobdsl/mobile-banking-backend.groovy`.
6. Run seed processing to create the pipeline job `mobile-banking-backend`.
