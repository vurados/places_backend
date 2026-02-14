pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build & Push') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-id', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh 'docker build -t vuardos/places-backend:jenkimage -f docker/Dockerfile .'
                        // Perform login using single quotes to avoid Groovy interpolation and rely on env vars
                        sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                        sh 'docker push vuardos/places-backend:jenkimage'
                    }
                }
            }
        }
    }
}
