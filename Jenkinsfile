pipeline {
  agent any

  parameters {
    string(name: 'APP_NAME', defaultValue: 'mobile-banking-backend', description: 'Container image/application name')
    booleanParam(name: 'ENABLE_CD', defaultValue: false, description: 'Deploy app after successful build on main branch')
  }

  environment {
    APP_NAME = "${params.APP_NAME ?: env.APP_NAME ?: 'mobile-banking-backend'}"
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    IMAGE = "${APP_NAME}:${IMAGE_TAG}"
  }

  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Setup Python') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -euo pipefail
              python3 -m venv .venv
              . .venv/bin/activate
              pip install --upgrade pip
              pip install -r app/requirements.txt
              pip install pytest
              mkdir -p reports
            '''
          } else {
            bat '''
              python -m venv .venv
              call .venv\\Scripts\\activate
              python -m pip install --upgrade pip
              pip install -r app\\requirements.txt
              pip install pytest
              if not exist reports mkdir reports
            '''
          }
        }
      }
    }

    stage('Unit Tests') {
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -euo pipefail
              . .venv/bin/activate
              pytest app/test_app.py -q --junitxml=reports/pytest.xml
            '''
          } else {
            bat '''
              call .venv\\Scripts\\activate
              pytest app\\test_app.py -q --junitxml=reports\\pytest.xml
            '''
          }
        }
      }
    }

    stage('Build Container') {
      steps {
        script {
          if (isUnix()) {
            sh 'docker build -t ${IMAGE} .'
          } else {
            bat 'docker build -t %IMAGE% .'
          }
        }
      }
    }

    stage('Deploy (CD)') {
      when {
        allOf {
          branch 'main'
          expression { return params.ENABLE_CD }
        }
      }
      steps {
        script {
          if (isUnix()) {
            sh '''
              set -euo pipefail
              docker compose up -d app
              curl -fsS http://localhost:8080/health
            '''
          } else {
            bat '''
              docker compose up -d app
              powershell -NoProfile -Command "(Invoke-WebRequest -UseBasicParsing http://localhost:8080/health -TimeoutSec 20).StatusCode"
            '''
          }
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
