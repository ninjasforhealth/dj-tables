podTemplate(
  containers: [
    containerTemplate(name: 'python', image: 'python:alpine', ttyEnabled: true, command: 'cat')
  ]
) {
  node(POD_LABEL) {
    stage('Checkout') {
      checkout scm
    }
    container('python') {
      stage('Install') {
        sh 'pip install tox'
      }
      stage('Test') {
        sh 'tox'
      }
    }
  }
}
