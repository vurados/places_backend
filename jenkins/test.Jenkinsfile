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
                sh 'docker build -t vurados/places-backend:jenkimage -f docker/Dockerfile .'
                sh 'docker tag vurados/places-backend:jenkimage vurados/places-backend:jenkimage'
                sh 'docker push vurados/places-backend:jenkimage'
            }
        }
    }
}
