pipeline {
  agent {
    kubernetes {
      yamlFile 'pod-template.yaml'
    }
  }
  environment {
    FLIT_USERNAME = '@token'
    FLIT_PASSWORD = credentials('pypi_access_token')
  }
  triggers {
    pollSCM('*/2 * * * *')
  }
  stages {
    stage('Checkout') {
      checkout scm
    }
    container('python') {
      stage('Test') {
        steps {
          sh 'tox'
        }
      }
      stage('Publish') {
        steps {
          sh 'flit publish'
        }
      }
    }
  }
}
