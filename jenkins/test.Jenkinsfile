pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build Image') {
            steps {
                sh 'pwd'
                sh 'ls -l'
                script {
                    sh "docker build -t vurados/places-backend:jenkimage -f docker/Dockerfile ."
                }
            }
        }
    }
}
