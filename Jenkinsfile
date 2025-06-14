pipeline {
    agent any
    parameters {
        // Backend Parameters
        string(name: 'BACKEND_BUILD_IMAGE', defaultValue: 'flask_backend_image', description: 'my flask backend image name')
        string(name: 'BACKEND_IMAGE_TAG', defaultValue: 'latest', description: 'my BACKEND image tag')
        string(name: 'DOCKERHUB_BACKEND_REPO_NAME', defaultValue: 'simple-todo-flask-backend', description: 'docker hub repository name for the BACKEND')
        string(name: 'MASTER_USERNAME', defaultValue: '', description: 'Enter the DB master username')
        password(name: 'DB_PASSWORD', defaultValue: '', description: 'Enter the DB password')
        string(name: 'DB_ENDPOINT', defaultValue: '', description: 'Enter the DB endpoint')
        string(name: 'DB_INSTANCE_NAME', defaultValue: '', description: 'Enter the DB instance name')

        // Frontend Parameters
        string(name: 'FRONTEND_BUILD_IMAGE', defaultValue: 'flask_frontend_image', description: 'my flask frontend image name')
        string(name: 'FRONTEND_IMAGE_TAG', defaultValue: 'latest', description: 'my frontend image tag')
        string(name: 'DOCKERHUB_FRONTEND_REPO_NAME', defaultValue: 'simple-todo-flask-frontend', description: 'docker hub repository name for the FRONTEND')
        string(name: 'BACKEND_URL', defaultValue: '', description: 'Backend url made up of the protocol and host')
    }
    stages {
        stage('Validate Backend Parameters') {
            steps {
                script {
                    // Seed env from params
                    env.MASTER_USERNAME  = params.MASTER_USERNAME
                    env.DB_PASSWORD      = params.DB_PASSWORD
                    env.DB_ENDPOINT      = params.DB_ENDPOINT
                    env.DB_INSTANCE_NAME = params.DB_INSTANCE_NAME

                    // Loop until all are provided
                    while (!env.MASTER_USERNAME?.trim() || !env.DB_PASSWORD?.trim() || !env.DB_ENDPOINT?.trim() || !env.DB_INSTANCE_NAME?.trim()) {
                        echo "⚠️ Missing backend params. Please fill in all fields."
                        def userInput = input(
                            id: 'BackendParams',
                            message: 'Enter missing Backend configuration',
                            parameters: [
                                string(name: 'MASTER_USERNAME', defaultValue: env.MASTER_USERNAME ?: '', description: 'DB master username'),
                                password(name: 'DB_PASSWORD', defaultValue: env.DB_PASSWORD ?: '', description: 'DB password'),
                                string(name: 'DB_ENDPOINT', defaultValue: env.DB_ENDPOINT ?: '', description: 'DB endpoint'),
                                string(name: 'DB_INSTANCE_NAME', defaultValue: env.DB_INSTANCE_NAME ?: '', description: 'DB instance name')
                            ]
                        )
                        env.MASTER_USERNAME  = userInput.MASTER_USERNAME
                        env.DB_PASSWORD      = userInput.DB_PASSWORD
                        env.DB_ENDPOINT      = userInput.DB_ENDPOINT
                        env.DB_INSTANCE_NAME = userInput.DB_INSTANCE_NAME
                    }
                    echo "✅ All backend parameters provided."
                }
            }
        }

        stage('Build our Backend Image') {
            steps {
                dir('backend') {
                    sh 'ls -la'
                    sh '''
                        echo "Updating parameters.py with database configuration..."
                        sed -i 's/^master_username = .*/master_username = "${MASTER_USERNAME}"/' parameters.py
                        sed -i 's/^db_password = .*/db_password = "${DB_PASSWORD}"/' parameters.py
                        sed -i 's|^endpoint = .*|endpoint = "${DB_ENDPOINT}"|' parameters.py
                        sed -i 's/^db_instance_name = .*/db_instance_name = "${DB_INSTANCE_NAME}"/' parameters.py
                        echo "Parameters updated. Building Docker image..."
                    '''
                    sh "docker build -t ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG} ."
                }
            }
        }

        // stage('Backend Acceptance Tests') {
        //     steps {
        //         script {
        //             try {
        //                 echo "Starting backend container for testing..."
        //                 sh "docker run -d -p 5000:5000 --name flask_backend_container ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG}"
        //                 sleep 10
        //                 echo "Testing backend endpoint..."
        //                 def statusCode = sh(script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000", returnStdout: true).trim()
        //                 if (statusCode != '200') {
        //                     error "Backend HTTP request failed with status code: ${statusCode}"
        //                 } else {
        //                     echo "Backend HTTP request successful with status code: ${statusCode}"
        //                 }
        //             } finally {
        //                 echo "Cleaning up backend test container..."
        //                 sh "docker rm -f flask_backend_container || true"
        //             }
        //         }
        //     }
        // }
        //THE CODE ABOVE WONT WORK AND LEAD TO ERRORS BECAUSE THE BACKEND REQUIRES PARAMS LKE THE MASTER_USERNAME,... AND NOT HAVING THEM SET SINCE THE TEST IS MADE LOCALLY SHALL LEAD TO ERRORS EXCEPT IF YOU PREPARE A LOCAL DB FOR IT THAT SHALL MATCH ITS CREDENTIALS
        stage('Push Backend Image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: '550b2578-f31d-4312-adbd-f0714cb4d0fe', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh "docker tag ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG} ${DOCKERHUB_USER}/${params.DOCKERHUB_BACKEND_REPO_NAME}:${params.BACKEND_IMAGE_TAG}"
                    sh "docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASS}"
                    sh "docker push ${DOCKERHUB_USER}/${params.DOCKERHUB_BACKEND_REPO_NAME}:${params.BACKEND_IMAGE_TAG}"
                }
            }
        }

        stage('Validate Frontend Parameters') {
            steps {
                script {
                    env.BACKEND_URL = params.BACKEND_URL
                    while (!env.BACKEND_URL?.trim()) {
                        echo "⚠️ Backend URL is missing—please provide it."
                        def userInput = input(
                            id: 'FrontendParams',
                            message: 'Enter Backend URL for Frontend build',
                            parameters: [
                                string(name: 'BACKEND_URL', defaultValue: env.BACKEND_URL ?: '', description: 'Protocol and host (e.g., http://your-backend:5000)')
                            ]
                        )
                        env.BACKEND_URL = userInput.BACKEND_URL
                    }
                    echo "✅ Frontend will use BACKEND_URL: ${env.BACKEND_URL}"
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                dir('frontend') {
                    sh 'ls -la'
                    sh '''
                        echo "Updating frontend app.py with backend URL: ${env.BACKEND_URL}"
                        sed -i "s#http://localhost:5000#${env.BACKEND_URL}#g" app.py
                        echo "Frontend configuration updated. Building Docker image..."
                    '''
                    sh "docker build -t ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG} ."
                }
            }
        }

        stage('Frontend Acceptance Tests') {
            steps {
                script {
                    try {
                        echo "Starting frontend container for testing..."
                        sh "docker run -d -p 4000:4000 --name flask_frontend_container ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG}"
                        sleep 10
                        echo "Testing frontend endpoint..."
                        def statusCode = sh(script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:4000", returnStdout: true).trim()
                        if (statusCode != '200') {
                            error "Frontend HTTP request failed with status code: ${statusCode}"
                        } else {
                            echo "Frontend HTTP request successful with status code: ${statusCode}"
                        }
                    } finally {
                        echo "Cleaning up frontend test container..."
                        sh "docker rm -f flask_frontend_container || true"
                    }
                }
            }
        }

        stage('Push Frontend Image to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: '550b2578-f31d-4312-adbd-f0714cb4d0fe', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    sh "docker tag ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG} ${DOCKERHUB_USER}/${params.DOCKERHUB_FRONTEND_REPO_NAME}:${params.FRONTEND_IMAGE_TAG}"
                    sh "docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASS}"
                    sh "docker push ${DOCKERHUB_USER}/${params.DOCKERHUB_FRONTEND_REPO_NAME}:${params.FRONTEND_IMAGE_TAG}"
                }
            }
        }
    }

    post {
        always {
            // Clean up any remaining containers
            sh "docker rm -f flask_backend_container flask_frontend_container || true"
        }
    }
}
