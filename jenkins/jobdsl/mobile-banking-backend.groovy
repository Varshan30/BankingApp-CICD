pipelineJob('mobile-banking-backend') {
  description('CI/CD pipeline for the Mobile Banking Backend project.')

  properties {
    disableConcurrentBuilds()
  }

  parameters {
    stringParam('APP_NAME', 'mobile-banking-backend', 'Container image/application name')
  }

  definition {
    cpsScm {
      scm {
        git {
          remote {
            url('https://github.com/your-org/Devops.git')
          }
          branch('*/main')
        }
      }
      scriptPath('Jenkinsfile')
      lightweight(true)
    }
  }
}