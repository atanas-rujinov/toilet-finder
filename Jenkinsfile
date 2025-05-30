pipeline {
    agent any

    environment {
        IMAGE_NAME = "toilet-finder"
        DOCKER_TAG = "latest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:${DOCKER_TAG}")
                }
            }
        }

        stage('Test Docker Image') {
            steps {
                script {
                    docker.image("${IMAGE_NAME}:${DOCKER_TAG}").inside {
                        // You can run test commands here if you add any tests to your app
                        sh 'python --version'  // Example command just to check container runs
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up...'
            sh "docker system prune -f"
        }
    }
}

