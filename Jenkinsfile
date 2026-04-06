pipeline {
  agent any

  environment {
    APP_NAME = "mobile-banking-backend"
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    REGISTRY = "${env.DOCKER_REGISTRY}"
    IMAGE = "${APP_NAME}:${IMAGE_TAG}"
    DEPLOY_TARGET = "minikube"
    MINIKUBE_PROFILE = "minikube"
    INGRESS_MANIFEST = "k8s/ingress.minikube.yaml"
    APPLY_INGRESS = "false"
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
          if (env.DEPLOY_TARGET == 'minikube') {
            env.REGISTRY = ""
            env.IMAGE = "${env.APP_NAME}:${env.IMAGE_TAG}"
          } else if (registry) {
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
          expression { return env.DEPLOY_TARGET != 'minikube' && env.REGISTRY?.trim() }
        }
      }
      steps {
        script {
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

    stage('Minikube Preflight') {
      when {
        expression { return env.DEPLOY_TARGET == 'minikube' }
      }
      steps {
        sh '''
          set -euo pipefail
          minikube -p ${MINIKUBE_PROFILE} status
          kubectl config use-context ${MINIKUBE_PROFILE} || true
          minikube -p ${MINIKUBE_PROFILE} addons enable ingress
          minikube -p ${MINIKUBE_PROFILE} addons enable metrics-server || true
          kubectl version --request-timeout=15s
        '''
      }
    }

    stage('Load Image Into Minikube') {
      when {
        expression { return env.DEPLOY_TARGET == 'minikube' }
      }
      steps {
        sh '''
          set -euo pipefail
          minikube -p ${MINIKUBE_PROFILE} image load ${IMAGE}
        '''
      }
    }

    stage('Validate Kubernetes Manifests') {
      when {
        expression { return env.DEPLOY_TARGET == 'minikube' }
      }
      steps {
        sh '''
          set -euo pipefail
          kubectl config use-context ${MINIKUBE_PROFILE} || true
          sed "s|REPLACE_WITH_IMAGE|${IMAGE}|g" k8s/deployment.yaml > reports/deployment.rendered.yaml
          kubectl apply --dry-run=client --validate=false --request-timeout=15s -f k8s/namespace.yaml
          kubectl apply --dry-run=client --validate=false --request-timeout=15s -f reports/deployment.rendered.yaml
          kubectl apply --dry-run=client --validate=false --request-timeout=15s -f k8s/service.yaml
          kubectl apply --dry-run=client --validate=false --request-timeout=15s -f k8s/networkpolicy.yaml
          kubectl apply --dry-run=client --validate=false --request-timeout=15s -f k8s/hpa.yaml
          if [ "${APPLY_INGRESS}" = "true" ]; then
            kubectl apply --dry-run=client --validate=false --request-timeout=15s -f ${INGRESS_MANIFEST}
          fi
        '''
      }
    }

    stage('Deploy to Minikube') {
      when {
        allOf {
          anyOf {
            branch 'main'
            branch 'master'
          }
          expression { return env.DEPLOY_TARGET == 'minikube' }
        }
      }
      steps {
        sh '''
          set -euo pipefail
          kubectl config use-context ${MINIKUBE_PROFILE} || true
          kubectl apply --validate=false --request-timeout=15s -f k8s/namespace.yaml
          sed "s|REPLACE_WITH_IMAGE|${IMAGE}|g" k8s/deployment.yaml | kubectl apply --validate=false --request-timeout=15s -f -
          kubectl apply --validate=false --request-timeout=15s -f k8s/service.yaml
          kubectl apply --validate=false --request-timeout=15s -f k8s/networkpolicy.yaml
          kubectl apply --validate=false --request-timeout=15s -f k8s/hpa.yaml
          if [ "${APPLY_INGRESS}" = "true" ]; then
            kubectl apply --validate=false --request-timeout=15s -f ${INGRESS_MANIFEST}
          fi
          kubectl -n banking rollout status deployment/banking-backend --timeout=120s
        '''
      }
    }

    stage('Post-Deploy Smoke Check') {
      when {
        allOf {
          anyOf {
            branch 'main'
            branch 'master'
          }
          expression { return env.DEPLOY_TARGET == 'minikube' }
        }
      }
      steps {
        sh '''
          set -euo pipefail
          kubectl config use-context ${MINIKUBE_PROFILE} || true
          kubectl -n banking get deploy banking-backend
          kubectl -n banking get pods -l app=banking-backend
          kubectl -n banking get svc banking-backend-service
          kubectl -n banking get ingress banking-backend-ingress || true
          minikube -p ${MINIKUBE_PROFILE} service banking-backend-service -n banking --url
        '''
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
