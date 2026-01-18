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
                bat '''
                REM Start container
                docker run -d -p %APP_PORT%:%APP_PORT% --name %CONTAINER_NAME% %IMAGE_NAME%:latest

                REM Wait for service to be up with retries
                SET RETRIES=20
                SET URL=http://localhost:%APP_PORT%/

                :RETRY
                curl %URL% > nul 2>&1
                IF %ERRORLEVEL% EQU 0 (
                    echo Service is up!
                    goto SUCCESS
                )
                SET /A RETRIES=%RETRIES%-1
                IF %RETRIES% GTR 0 (
                    echo Waiting for service...
                    TIMEOUT /T 3
                    GOTO RETRY
                )
                echo Service failed to start within timeout
                exit /b 1

                :SUCCESS
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
