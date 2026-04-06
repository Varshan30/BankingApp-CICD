# Jenkins Configuration Notes

This repository ships with a Jenkins Declarative Pipeline in `Jenkinsfile`.

Pipeline purpose: keep CI simple and beginner-friendly.

## 2. Configure Pipeline Job

Create a Jenkins Pipeline job and point it to this repository root `Jenkinsfile`.

The pipeline uses one parameter:

- `APP_NAME`

## 3. Agent Requirements

Jenkins agent must have:

- Docker
- Python 3 + pip

## 4. Pipeline Security Gates

- Unit tests with `pytest`

## 5. Pipeline Behavior

- Test report published from `reports/pytest.xml`
- Container image is built with Docker

Related setup guide:

- End-to-end checklist: `jenkins/jenkins-setup-runbook.md`

## 6. Ready-to-Import Automation Artifacts

This repository includes Jenkins automation bootstrap files:

- JCasC file: `jenkins/casc/jenkins.yaml`
- Job DSL file: `jenkins/jobdsl/mobile-banking-backend.groovy`

How to use:

1. Install plugins: Configuration as Code, Job DSL.
2. Set `CASC_JENKINS_CONFIG` to `jenkins/casc/jenkins.yaml` (or absolute path).
3. Start/restart Jenkins so JCasC applies.
4. Update repository URL in `jenkins/jobdsl/mobile-banking-backend.groovy`.
5. Run a seed job (or JCasC jobs import) to create pipeline job `mobile-banking-backend`.

Important:

- Replace default admin credentials via environment variables before production use.
