pipeline {
    agent any
    
    environment {
        
        GIT_REPO = 'https://github.com/ByronTopham/Friends4Lyfe.git'
        DOCKER_IMAGE = 'akanshapal/stock-calculator:latest'
        KUBE_NAMESPACE = 'jenkins' // Kubernetes namespace to deploy to
        AWS_CREDENTIALS_ID = 'aws-credentials-id'
    }

    stages {
        stage('Checkout Code') {
            steps {
                // Clone the Git repository
                git branch: 'main', credentialsId: 'git-credentials', url: "${GIT_REPO}"
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Run the Docker build command using bat (Windows batch command)
                    bat "docker build -t ${DOCKER_IMAGE} ."
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Add your test commands if applicable
                    bat 'echo Running tests...'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Replace 'dockerhub-credentials' with your Jenkins Docker credentials ID
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASS', usernameVariable: 'DOCKERHUB_USER')]) {
                        // Log in to Docker Hub or your Docker registry
                        bat "docker login -u %DOCKERHUB_USER% -p %DOCKERHUB_PASS%"
                        
                        // Push the Docker image
                        bat "docker push ${DOCKER_IMAGE}"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                withAWS(credentials: "${AWS_CREDENTIALS_ID}", region: 'us-west-2') {
			bat 'kubectl apply -f deployment.yaml'
			bat 'kubectl apply -f network-policy.yaml'
			bat 'kubectl get pods --show-labels'
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            cleanWs() // Clean workspace after the pipeline
        }
    }
}
