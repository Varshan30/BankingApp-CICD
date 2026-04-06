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
- Linux or Windows agent is supported by this pipeline

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

## 7. Run Jenkins Now (Quick Start)

1. Start Jenkins using one command:

	Windows PowerShell:

	.\\scripts\\start-jenkins.ps1

	Linux/macOS:

	./scripts/start-jenkins.sh

	Or manual Docker command:

	docker run -d --name jenkins -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts

2. Open Jenkins:

	http://localhost:8080

3. Create Pipeline job:

	- New Item -> Pipeline -> name: mobile-banking-backend
	- Pipeline Definition: Pipeline script from SCM
	- SCM: Git
	- Repository URL: your GitHub repository
	- Script Path: Jenkinsfile

4. Build Now to execute tests and Docker image build.
