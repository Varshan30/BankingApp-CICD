pipeline {
  agent any

  environment {
    APP_NAME = "mobile-banking-backend"
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    REGISTRY = "${env.DOCKER_REGISTRY}"
    IMAGE = "${APP_NAME}:${IMAGE_TAG}"
    AWS_DEFAULT_REGION = "${env.AWS_REGION}"
    TERRAFORM_DIR = "terraform/aws"
    ANSIBLE_PLAYBOOK = "ansible/playbooks/site.yml"
    ANSIBLE_INVENTORY = "ansible/inventory/hosts.ini"
  }

  options {
    timestamps()
    ansiColor('xterm')
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Resolve Build Image Reference') {
      steps {
        script {
          def registry = env.DOCKER_REGISTRY?.trim()
          if (registry) {
            env.REGISTRY = registry
            env.IMAGE = "${registry}/${env.APP_NAME}:${env.IMAGE_TAG}"
          } else {
            env.REGISTRY = ""
            env.IMAGE = "${env.APP_NAME}:${env.IMAGE_TAG}"
          }
          echo "Resolved image reference: ${env.IMAGE}"
        }
      }
    }

    stage('Terraform Format + Validate') {
      when {
        expression { return env.TERRAFORM_ENABLED == 'true' }
      }
      steps {
        dir("${env.TERRAFORM_DIR}") {
          sh '''
            set -euo pipefail
            terraform fmt -check -recursive
            terraform init
            terraform validate
          '''
        }
      }
    }

    stage('Terraform Plan') {
      when {
        expression { return env.TERRAFORM_ENABLED == 'true' }
      }
      steps {
        dir("${env.TERRAFORM_DIR}") {
          sh '''
            set -euo pipefail
            terraform plan -out=tfplan
          '''
        }
      }
    }

    stage('Terraform Apply') {
      when {
        allOf {
          anyOf {
            branch 'main'
            branch 'master'
          }
          expression { return env.TERRAFORM_ENABLED == 'true' && env.TERRAFORM_AUTO_APPLY == 'true' }
        }
      }
      steps {
        dir("${env.TERRAFORM_DIR}") {
          sh '''
            set -euo pipefail
            terraform apply -auto-approve tfplan
          '''
        }
      }
    }

    stage('Resolve Infra Outputs') {
      when {
        expression { return env.TERRAFORM_ENABLED == 'true' }
      }
      steps {
        script {
          env.EKS_CLUSTER_NAME = sh(
            script: "cd ${env.TERRAFORM_DIR} && terraform output -raw eks_cluster_name",
            returnStdout: true
          ).trim()

          def ecrRepo = sh(
            script: "cd ${env.TERRAFORM_DIR} && terraform output -raw ecr_repository_url",
            returnStdout: true
          ).trim()

          if (!env.DOCKER_REGISTRY?.trim() && ecrRepo) {
            env.REGISTRY = ecrRepo
            env.IMAGE = "${ecrRepo}:${env.IMAGE_TAG}"
          }

          echo "Resolved cluster: ${env.EKS_CLUSTER_NAME}"
          echo "Resolved image reference: ${env.IMAGE}"
        }
      }
    }

    stage('Run Ansible Bootstrap (Optional)') {
      when {
        expression { return env.ANSIBLE_ENABLED == 'true' }
      }
      steps {
        sh '''
          set -euo pipefail
          test -f "${ANSIBLE_PLAYBOOK}"
          test -f "${ANSIBLE_INVENTORY}"
          ansible-playbook -i "${ANSIBLE_INVENTORY}" "${ANSIBLE_PLAYBOOK}"
        '''
      }
    }

    stage('Setup Toolchain') {
      steps {
        sh '''
          set -euo pipefail
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r app/requirements.txt
          pip install pytest bandit pip-audit
          mkdir -p reports
        '''
      }
    }

    stage('Unit Tests') {
      steps {
        sh '''
          set -euo pipefail
          . .venv/bin/activate
          pytest app/test_app.py -q --junitxml=reports/pytest.xml
        '''
      }
    }

    stage('SAST Scan (Bandit)') {
      steps {
        sh '''
          set -euo pipefail
          . .venv/bin/activate
          bandit -r app -x app/test_app.py -lll -f json -o reports/bandit.json
        '''
      }
    }

    stage('Dependency Scan (pip-audit)') {
      steps {
        sh '''
          set -euo pipefail
          . .venv/bin/activate
          pip-audit -r app/requirements.txt -f json -o reports/pip-audit.json
        '''
      }
    }

    stage('Build Container') {
      steps {
        sh 'docker build -t ${IMAGE} .'
      }
    }

    stage('Container Scan (Trivy)') {
      steps {
        sh '''
          set -euo pipefail
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy:0.57.1 image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE} > reports/trivy.txt
        '''
      }
    }

    stage('Push Container') {
      when {
        allOf {
          anyOf {
            branch 'main'
            branch 'master'
          }
          expression { return env.REGISTRY?.trim() }
        }
      }
      steps {
        script {
          if (env.REGISTRY.contains('amazonaws.com') && env.AWS_CREDENTIALS_ID?.trim() && env.AWS_REGION?.trim()) {
            withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: env.AWS_CREDENTIALS_ID]]) {
              sh '''
                set -euo pipefail
                aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${REGISTRY}
                docker push ${IMAGE}
              '''
            }
          } else {
            withCredentials([usernamePassword(credentialsId: 'docker-registry-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
              sh '''
                set -euo pipefail
                echo "$DOCKER_PASS" | docker login ${REGISTRY} -u "$DOCKER_USER" --password-stdin
                docker push ${IMAGE}
              '''
            }
          }
        }
      }
    }

    stage('Validate Kubernetes Manifests') {
      steps {
        sh '''
          set -euo pipefail
          sed "s|REPLACE_WITH_IMAGE|${IMAGE}|g" k8s/deployment.yaml > reports/deployment.rendered.yaml
          kubectl apply --dry-run=client -f k8s/namespace.yaml
          kubectl apply --dry-run=client -f reports/deployment.rendered.yaml
          kubectl apply --dry-run=client -f k8s/service.yaml
          kubectl apply --dry-run=client -f k8s/networkpolicy.yaml
          kubectl apply --dry-run=client -f k8s/hpa.yaml
          kubectl apply --dry-run=client -f k8s/ingress.yaml
        '''
      }
    }

    stage('Deploy to EKS') {
      when {
        allOf {
          anyOf {
            branch 'main'
            branch 'master'
          }
          expression { return env.AWS_CREDENTIALS_ID?.trim() && env.EKS_CLUSTER_NAME?.trim() && env.AWS_REGION?.trim() }
        }
      }
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: env.AWS_CREDENTIALS_ID]]) {
          sh '''
            set -euo pipefail
            aws eks update-kubeconfig --name ${EKS_CLUSTER_NAME} --region ${AWS_REGION}
            kubectl apply -f k8s/namespace.yaml
            kubectl apply -f k8s/cert-issuer.yaml
            sed "s|REPLACE_WITH_IMAGE|${IMAGE}|g" k8s/deployment.yaml | kubectl apply -f -
            kubectl apply -f k8s/service.yaml
            kubectl apply -f k8s/networkpolicy.yaml
            kubectl apply -f k8s/hpa.yaml
            kubectl apply -f k8s/ingress.yaml
            kubectl -n banking rollout status deployment/banking-backend --timeout=120s
          '''
        }
      }
    }

    stage('Post-Deploy Smoke Check') {
      when {
        allOf {
          anyOf {
            branch 'main'
            branch 'master'
          }
          expression { return env.AWS_CREDENTIALS_ID?.trim() && env.EKS_CLUSTER_NAME?.trim() && env.AWS_REGION?.trim() }
        }
      }
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: env.AWS_CREDENTIALS_ID]]) {
          sh '''
            set -euo pipefail
            aws eks update-kubeconfig --name ${EKS_CLUSTER_NAME} --region ${AWS_REGION}
            kubectl -n banking get deploy banking-backend
            kubectl -n banking get pods -l app=banking-backend
            kubectl -n banking get svc banking-backend
            kubectl -n banking get ingress banking-backend-ingress || true
          '''
        }
      }
    }

  }

  post {
    always {
      junit testResults: 'reports/pytest.xml', allowEmptyResults: true
      archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
      cleanWs()
    }
  }
}
