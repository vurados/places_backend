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
                    docker.withRegistry('', 'dockerhub-id') {
                        def img = docker.build("vurados/places-backend:jenkimage -f docker/Dockerfile .")
                        img.push()
                    }
                }
            }
        }
    }
}
