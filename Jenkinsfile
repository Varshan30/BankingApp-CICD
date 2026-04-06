pipeline {
  agent any

  parameters {
    string(name: 'APP_NAME', defaultValue: 'mobile-banking-backend', description: 'Container image/application name')
  }

  environment {
    APP_NAME = "${params.APP_NAME ?: env.APP_NAME ?: 'mobile-banking-backend'}"
    IMAGE_TAG = "${env.BUILD_NUMBER}"
    IMAGE = "${APP_NAME}:${IMAGE_TAG}"
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

    stage('Setup Python') {
      steps {
        sh '''
          set -euo pipefail
          python3 -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r app/requirements.txt
          pip install pytest
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

    stage('Build Container') {
      steps {
        sh 'docker build -t ${IMAGE} .'
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
