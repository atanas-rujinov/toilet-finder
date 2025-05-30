pipeline {
    agent any

    environment {
        IMAGE_NAME = 'toilet-finder'
        CONTAINER_PORT = '5000'
    }

    stages {

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $IMAGE_NAME .'
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    // Stop old container if it exists
                    sh 'docker stop toilet-finder || true'
                    sh 'docker rm toilet-finder || true'

                    // Run new container
                    sh 'docker run -d -p 5000:5000 --name toilet-finder $IMAGE_NAME'
                }
            }
        }
    }
}
