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
    environment {
        DOCKER_USER = 'atahacr'
        REPO_NAME = 'toilet-finder'
        IMAGE_TAG = 'latest'
    }
    steps {
        withCredentials([string(credentialsId: 'DOCKER_HUB_PASSWORD', variable: 'DOCKER_PASSWORD')]) {
            script {
                def fullImageName = "${DOCKER_USER}/${REPO_NAME}:${IMAGE_TAG}"
                sh "echo ${DOCKER_PASSWORD} | docker login -u ${DOCKER_USER} --password-stdin"
                sh "docker tag ${REPO_NAME}:${IMAGE_TAG} ${fullImageName}"
                sh "docker push ${fullImageName}"
            }
        }
    }
}


stage('Deploy to Production') {
    steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'deploy-key', keyFileVariable: 'SSH_KEY')]) {
            sh '''
                ssh -i $SSH_KEY -o StrictHostKeyChecking=no -p 7822 deploy@192.168.14.129 'bash ~/deploy.sh'
            '''
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

