pipeline {
    agent any

    environment {
        IMAGE_NAME = "flight-price-api"
        CONTAINER_NAME = "flight-price-ci-test"
        APP_PORT = "8000"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %IMAGE_NAME%:latest -f Dockerfile ."
            }
        }

        stage('Run Container and Wait for Service') {
            steps {
                bat """
                docker run -d -p %APP_PORT%:%APP_PORT% --name %CONTAINER_NAME% %IMAGE_NAME%:latest

                SET RETRIES=20
                SET URL=http://localhost:%APP_PORT%/

                :RETRY
                curl --fail %URL%
                IF %ERRORLEVEL% EQU 0 (
                    echo Service is up!
                    goto SUCCESS
                )

                SET /A RETRIES-=1
                IF %RETRIES% GTR 0 (
                    echo Waiting for service...
                    ping 127.0.0.1 -n 4 > nul
                    goto RETRY
                )

                echo Service failed to start within timeout
                exit /b 1

                :SUCCESS
                """
            }
        }
    }

    post {
        always {
            bat """
            docker stop %CONTAINER_NAME% || exit 0
            docker rm %CONTAINER_NAME% || exit 0
            """
        }
    }
}
