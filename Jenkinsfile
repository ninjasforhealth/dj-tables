pipeline {
  agent {
    kubernetes {
      yamlFile 'pod-template.yaml'
    }
  }
  environment {
    FLIT_USERNAME = '__token__'
    FLIT_PASSWORD = credentials('pypi_access_token')
  }
  triggers {
    pollSCM('*/2 * * * *')
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Test') {
      steps {
        container('python') {
          sh 'tox'
        }
      }
    }
    stage('Publish') {
      steps {
        container('python') {
          sh 'flit publish'
        }
      }
    }
  }
}
