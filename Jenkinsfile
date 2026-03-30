pipeline {
  agent any

  environment {
    APP_NAME = "mobile-banking-backend"
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    REGISTRY = "${env.DOCKER_REGISTRY}"
    IMAGE = "${env.DOCKER_REGISTRY}/${APP_NAME}:${IMAGE_TAG}"
    AWS_DEFAULT_REGION = "${env.AWS_REGION}"
  }

  options {
    timestamps()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Unit Tests') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r app/requirements.txt
          pytest app/test_app.py -q
        '''
      }
    }

    stage('SAST Scan (Bandit)') {
      steps {
        sh '''
          . .venv/bin/activate
          pip install bandit
          bandit -r app -x app/test_app.py -lll
        '''
      }
    }

    stage('Dependency Scan (pip-audit)') {
      steps {
        sh '''
          . .venv/bin/activate
          pip install pip-audit
          pip-audit -r app/requirements.txt
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
          docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy:0.57.1 image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE}
        '''
      }
    }

    stage('Push Container') {
      when {
        expression { return env.DOCKER_REGISTRY?.trim() }
      }
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-registry-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "$DOCKER_PASS" | docker login ${REGISTRY} -u "$DOCKER_USER" --password-stdin
            docker push ${IMAGE}
          '''
        }
      }
    }

    stage('Deploy to EKS') {
      when {
        expression { return env.AWS_CREDENTIALS_ID?.trim() && env.EKS_CLUSTER_NAME?.trim() && env.AWS_REGION?.trim() }
      }
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: env.AWS_CREDENTIALS_ID]]) {
          sh '''
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

    stage('Install Monitoring and Logging') {
      when {
        expression { return env.DEPLOY_OBSERVABILITY == 'true' && env.AWS_CREDENTIALS_ID?.trim() && env.EKS_CLUSTER_NAME?.trim() && env.AWS_REGION?.trim() }
      }
      steps {
        withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: env.AWS_CREDENTIALS_ID]]) {
          sh '''
            aws eks update-kubeconfig --name ${EKS_CLUSTER_NAME} --region ${AWS_REGION}
            chmod +x scripts/install_observability.sh
            ./scripts/install_observability.sh
          '''
        }
      }
    }
  }

  post {
    always {
      cleanWs()
    }
  }
}
