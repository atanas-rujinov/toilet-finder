pipeline {
    agent any

   environment {
        IMAGE_NAME = "toilet-finder"
        DOCKER_TAG = "latest"
        DOCKER_HUB_USER = "atahacr"
        FULL_IMAGE_NAME = "${DOCKER_HUB_USER}/${IMAGE_NAME}:${DOCKER_TAG}"
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

        stage('Run Tests') {
            steps {
                script {
                    docker.image("${IMAGE_NAME}:${DOCKER_TAG}").inside {
                        sh 'pytest --maxfail=1 --disable-warnings -q'
                    }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'docker-hub-creds') {
                        docker.image("${IMAGE_NAME}:${DOCKER_TAG}").tag("${FULL_IMAGE_NAME}")
                            docker.image("${FULL_IMAGE_NAME}").push()
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

