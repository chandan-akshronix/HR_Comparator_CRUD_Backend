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
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    echo "📊 Starting SonarQube Code Quality Analysis..."
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    def scannerHome = tool 'sonar-scanner'
                    withSonarQubeEnv('sonar-scanner') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \
                              -Dsonar.projectKey=hr-backend-api \
                              -Dsonar.projectName='HR Backend API' \
                              -Dsonar.sources=. \
                              -Dsonar.python.coverage.reportPaths=coverage.xml \
                              -Dsonar.exclusions=**/*.pyc,**/migrations/**,**/__pycache__/**
                        """
                    }
                    echo "✅ SonarQube analysis submitted successfully"
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                script {
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    echo "⏳ Waiting for SonarQube Quality Gate result..."
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    timeout(time: 10, unit: 'MINUTES') {
                        def qg = waitForQualityGate()
                        echo "📊 Quality Gate Status: ${qg.status}"
                        if (qg.status != 'OK') {
                            error "❌ Quality Gate failed with status: ${qg.status}"
                        }
                    }
                    echo "✅ Quality Gate passed successfully"
                }
            }
        }
        
        stage('Trivy File System Scan') {
            steps {
                script {
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    echo "🔒 Running Trivy file system scan..."
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    sh """
                        trivy fs \
                          --severity HIGH,CRITICAL \
                          --exit-code 0 \
                          --format table \
                          .
                    """
                    echo "✅ Trivy file system scan completed"
                }
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
        
        stage('Trivy Image Scan') {
            steps {
                script {
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    echo "🔒 Running Trivy Docker image security scan..."
                    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    sh """
                        trivy image \
                          --severity HIGH,CRITICAL \
                          --exit-code 0 \
                          --format table \
                          ${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}
                    """
                    echo "✅ Trivy image scan completed"
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
        
        /* COMMENTED OUT - Deploy to AKS stage
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
        */ // End of commented Deploy to AKS stage
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
            Status: Images pushed to ACR successfully
            Note: Deploy to AKS stage is commented out
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
