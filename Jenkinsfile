pipeline {
    agent any
    
    environment {
        ACR_NAME = 'hracrregistry' // Will be output from Terraform
        ACR_LOGIN_SERVER = 'hracrregistry.azurecr.io'
        IMAGE_NAME = 'backend-api'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
        SONARQUBE_SERVER = 'http://4.213.4.181:9000' // Jenkins configured server name
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "✅ Code checked out successfully"
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'SonarScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=hr-backend-api \
                              -Dsonar.projectName='HR Backend API' \
                              -Dsonar.sources=. \
                              -Dsonar.python.coverage.reportPaths=coverage.xml \
                              -Dsonar.exclusions=**/*.pyc,**/migrations/**
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
                echo "✅ Quality Gate passed"
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker images for ACR..."
                    sh """
                        docker build -t ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} .
                        docker tag ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest
                    """
                    echo "✅ Docker images built successfully"
                }
            }
        }
        
        stage('Security Scan - Trivy') {
            steps {
                script {
                    echo "Running Trivy security scan..."
                    sh """
                        trivy image \
                          --severity HIGH,CRITICAL \
                          --exit-code 0 \
                          --format table \
                          ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}
                    """
                    echo "✅ Security scan completed"
                }
            }
        }
        
        stage('Push to Azure Container Registry') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'acr-credentials', usernameVariable: 'ACR_USERNAME', passwordVariable: 'ACR_PASSWORD')]) {
                        sh """
                            echo \$ACR_PASSWORD | docker login ${ACR_LOGIN_SERVER} -u \$ACR_USERNAME --password-stdin
                            docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest
                            docker logout ${ACR_LOGIN_SERVER}
                        """
                        echo "✅ Images pushed to Azure Container Registry"
                    }
                }
            }
        }
        
        stage('Deploy to AKS') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh """
                            export KUBECONFIG=\$KUBECONFIG
                            
                            # Update deployment with new image from ACR
                            kubectl set image deployment/backend-api \
                              backend-api=${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG} \
                              -n hr-app
                            
                            # Wait for rollout to complete
                            kubectl rollout status deployment/backend-api -n hr-app --timeout=5m
                            
                            # Verify deployment
                            kubectl get pods -n hr-app -l app=backend-api
                        """
                        echo "✅ Deployment successful"
                    }
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
            sh "docker system prune -f || true"
        }
        success {
            echo """
            ========================================
            ✅ Backend API Pipeline Successful!
            ========================================
            Image: ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}
            Registry: Azure Container Registry
            Deployed to: hr-app namespace
            ========================================
            """
        }
        failure {
            echo """
            ========================================
            ❌ Backend API Pipeline Failed!
            ========================================
            Check the logs above for details
            ========================================
            """
        }
    }
}
