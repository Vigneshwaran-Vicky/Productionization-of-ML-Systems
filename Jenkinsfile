pipeline {
    agent any

    environment {
        IMAGE_NAME = "flight-price-api"
        CONTAINER_NAME = "flight-price-ci-test"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:latest -f Dockerfile .'
            }
        }

        stage('Run Container') {
            steps {
                bat '''
                docker run -d -p 8501:8501 --name flight-price-ci-test flight-price-api:latest
                ping 127.0.0.1 -n 16 > nul
                curl --retry 10 --retry-delay 3 http://localhost:8501/
                '''
            }
        }
    }

    post {
        always {
            bat '''
            docker stop %CONTAINER_NAME% || exit 0
            docker rm %CONTAINER_NAME% || exit 0
            '''
        }
    }
}
