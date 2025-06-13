pipeline {
    agent any
    parameters {
        //Backend Parameters----------------------------------------------------------------------------------------------
        string(name: 'BACKEND_BUILD_IMAGE', defaultValue: 'flask_backend_image', description: 'my flask backend image name')
        string(name: 'BACKEND_IMAGE_TAG',   defaultValue: 'latest',                 description: 'my BACKEND image tag')
        string(name: 'DOCKERHUB_BACKEND_REPO_NAME', defaultValue: 'simple-todo-flask-backend', description: 'docker hub repository name for the BACKEND')
        // Provide empty defaults or instruct in the description
        string(name: 'MASTER_USERNAME', defaultValue: '', description: 'Enter the DB master username')
        password(name: 'DB_PASSWORD', defaultValue: '', description: 'Enter the DB password')
        string(name: 'DB_ENDPOINT', defaultValue: '', description: 'Enter the DB endpoint')
        string(name: 'DB_INSTANCE_NAME', defaultValue: '', description: 'Enter the DB instance name')

        //Frontend Parameters----------------------------------------------------------------------------------------------
        string(name: 'FRONTEND_BUILD_IMAGE', defaultValue: 'flask_frontend_image', description: 'my flask frontend image name')
        string(name: 'FRONTEND_IMAGE_TAG',   defaultValue: 'latest',                 description: 'my frontend image tag')
        string(name: 'DOCKERHUB_FRONTEND_REPO_NAME', defaultValue: 'simple-todo-flask-frontend', description: 'docker hub repository name for the FRONTEND')
        // Provide empty defaults or instruct in the description
        string(name: 'BACKEND_URL', defaultValue: '', description: 'Backend url made up of the protocol and host')
    }
    stages {
        stage('Validate Parameters') {
            steps {
                script {
                    echo "Validating backend parameters..."
                    echo "MASTER_USERNAME: '${params.MASTER_USERNAME}'"
                    echo "DB_ENDPOINT: '${params.DB_ENDPOINT}'"
                    echo "DB_INSTANCE_NAME: '${params.DB_INSTANCE_NAME}'"
                    
                    // Check if any parameter is empty and ask for input if needed
                    if (!params.MASTER_USERNAME || params.MASTER_USERNAME.trim().isEmpty() ||
                        !params.DB_PASSWORD || params.DB_PASSWORD.trim().isEmpty() ||
                        !params.DB_ENDPOINT || params.DB_ENDPOINT.trim().isEmpty() ||
                        !params.DB_INSTANCE_NAME || params.DB_INSTANCE_NAME.trim().isEmpty()) {

                        echo "Some backend parameters are missing, requesting user input..."
                        def userInput = input(
                            id: 'userInput', 
                            message: 'Some required backend parameters are missing. Please provide the following:', 
                            parameters: [
                                string(name: 'MASTER_USERNAME', defaultValue: params.MASTER_USERNAME ?: '', description: 'DB master username'),
                                password(name: 'DB_PASSWORD', defaultValue: params.DB_PASSWORD ?: '', description: 'DB password'),
                                string(name: 'DB_ENDPOINT', defaultValue: params.DB_ENDPOINT ?: '', description: 'DB endpoint'),
                                string(name: 'DB_INSTANCE_NAME', defaultValue: params.DB_INSTANCE_NAME ?: '', description: 'DB instance name')
                            ]
                        )
                        // Override the empty parameters with the input values
                        env.MASTER_USERNAME = userInput.MASTER_USERNAME
                        env.DB_PASSWORD = userInput.DB_PASSWORD
                        env.DB_ENDPOINT = userInput.DB_ENDPOINT
                        env.DB_INSTANCE_NAME = userInput.DB_INSTANCE_NAME
                    } else {
                        echo "All backend parameters provided, proceeding..."
                        // Assign parameters to environment variables for easier use later
                        env.MASTER_USERNAME = params.MASTER_USERNAME
                        env.DB_PASSWORD = params.DB_PASSWORD
                        env.DB_ENDPOINT = params.DB_ENDPOINT
                        env.DB_INSTANCE_NAME = params.DB_INSTANCE_NAME
                    }
                    
                    echo "Backend validation complete."
                }
            }
        }
        stage('Build our Backend Image') {
            steps {
                dir('backend') {  // Removed leading slash
                    sh 'ls -la'
                    // Modify your parameters.py file with the provided environment variables
                    sh """
                        echo "Updating parameters.py with database configuration..."
                        sed -i 's/^master_username = .*/master_username = "${MASTER_USERNAME}"/' parameters.py
                        sed -i 's/^db_password = .*/db_password = "${DB_PASSWORD}"/' parameters.py
                        sed -i 's|^endpoint = .*|endpoint = "${DB_ENDPOINT}"|' parameters.py
                        sed -i 's/^db_instance_name = .*/db_instance_name = "${DB_INSTANCE_NAME}"/' parameters.py
                        echo "Parameters updated. Building Docker image..."
                    """
                    // Build the Docker image
                    sh """
                       docker build \\
                         -t ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG} \\
                         .
                    """
                }
            }
        }
        stage("Backend Acceptance Tests") {
            steps {
                script {
                    try {
                        echo "Starting backend container for testing..."
                        // Start container
                        sh "docker run -d -p 5000:5000 --name flask_backend_container ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG}"
                        
                        // Give container time to start
                        echo "Waiting for container to start..."
                        sh "sleep 10"
                        
                        // Test with curl using localhost instead of container IP
                        echo "Testing backend endpoint..."
                        def statusCode = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:5000",
                            returnStdout: true
                        ).trim()
                        
                        // Validate status code (200 is OK)
                        if (statusCode != "200") {
                            error "Backend HTTP request failed with status code: ${statusCode}"
                        } else {
                            echo "Backend HTTP request successful with status code: ${statusCode}"
                        }
                    } finally {
                        // Always clean up the container
                        echo "Cleaning up backend test container..."
                        sh "docker rm -f flask_backend_container || true"
                    }
                }
            }
        }

        stage("Push Backend Image to Docker Hub") {
            steps {
                // Use Jenkins credentials (create a 'dockerhub-credentials' with your Docker Hub username/password)
                withCredentials([usernamePassword(
                    credentialsId: '550b2578-f31d-4312-adbd-f0714cb4d0fe',
                    usernameVariable: 'DOCKERHUB_USER', 
                    passwordVariable: 'DOCKERHUB_PASS'
                    )]) {
                    sh "echo 'Tagging backend image for Docker Hub push...'"
                    sh "docker tag ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG} ${DOCKERHUB_USER}/${params.DOCKERHUB_BACKEND_REPO_NAME}:${params.BACKEND_IMAGE_TAG}"
                    sh "echo 'Logging in to Docker Hub as ${DOCKERHUB_USER}'"
                    sh "docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASS}"
                    sh "echo 'Pushing backend image to Docker Hub...'"
                    sh "docker push ${DOCKERHUB_USER}/${params.DOCKERHUB_BACKEND_REPO_NAME}:${params.BACKEND_IMAGE_TAG}"
                }
            }
        }
        
        //Frontend stages-------------------------------------------------------------------------------------
       
        stage("Validate Frontend Parameters"){
            steps{
                script{
                    echo "Validating frontend parameters..."
                    echo "BACKEND_URL: '${params.BACKEND_URL}'"
                    
                    if (!params.BACKEND_URL || params.BACKEND_URL.trim().isEmpty()) {
                        echo "Backend URL is missing, requesting user input..."
                        def userInput = input(
                            id: 'frontend_input',
                            message: 'The Backend URL is required to proceed with frontend build',
                            parameters: [
                                string(name: 'BACKEND_URL', defaultValue: params.BACKEND_URL ?: '', description: 'Backend url made up of the protocol and host (e.g., http://your-backend-host:5000)')
                            ]
                        )
                        env.BACKEND_URL = userInput.BACKEND_URL
                    } else {
                        env.BACKEND_URL = params.BACKEND_URL
                    }
                    
                    echo "Frontend validation complete. Backend URL: ${env.BACKEND_URL}"
                }
            }
        }

        stage("Build Frontend Image") {
            steps {
                // switch into your frontend folder
                dir('frontend') {  // Removed leading slash
                    // list files (optional sanity check)
                    sh 'ls -la'  
                    //update the frontend app.py endpoints to reflect the backend url 
                    sh """
                        echo "Updating frontend app.py with backend URL: ${env.BACKEND_URL}"
                        sed -i "s#http://localhost:5000#${env.BACKEND_URL}#g" app.py
                        echo "Frontend configuration updated. Building Docker image..."
                    """
                    // build with the name and tag from your parameters
                    sh """
                        docker build \\
                            -t ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG} \\
                            .
                    """
                }
            }
        }
        
        stage("Frontend Acceptance Tests") {
            steps {
                script {
                    try {
                        echo "Starting frontend container for testing..."
                        // Start container
                        sh "docker run -d -p 4000:4000 --name flask_frontend_container ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG}"
                        
                        // Give container time to start
                        echo "Waiting for frontend container to start..."
                        sh "sleep 10"
                        
                        // Test with curl using localhost instead of container IP
                        echo "Testing frontend endpoint..."
                        def statusCode = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://localhost:4000",
                            returnStdout: true
                        ).trim()
                        
                        // Validate status code (200 is OK)
                        if (statusCode != "200") {
                            error "Frontend HTTP request failed with status code: ${statusCode}"
                        } else {
                            echo "Frontend HTTP request successful with status code: ${statusCode}"
                        }
                    } finally {
                        // Always clean up the container
                        echo "Cleaning up frontend test container..."
                        sh "docker rm -f flask_frontend_container || true"
                    }
                }
            }
        }
        
        stage("Push Frontend Image to Docker Hub") {
            steps {
                // Use Jenkins credentials (create a 'dockerhub-credentials' with your Docker Hub username/password)
                withCredentials([usernamePassword(
                    credentialsId: '550b2578-f31d-4312-adbd-f0714cb4d0fe',
                    usernameVariable: 'DOCKERHUB_USER', 
                    passwordVariable: 'DOCKERHUB_PASS'
                    )]) {
                    sh "echo 'Tagging frontend image for Docker Hub push...'"
                    sh "docker tag ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG} ${DOCKERHUB_USER}/${params.DOCKERHUB_FRONTEND_REPO_NAME}:${params.FRONTEND_IMAGE_TAG}"
                    sh "echo 'Logging in to Docker Hub as ${DOCKERHUB_USER}'"
                    sh "docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASS}"
                    sh "echo 'Pushing frontend image to Docker Hub...'"
                    sh "docker push ${DOCKERHUB_USER}/${params.DOCKERHUB_FRONTEND_REPO_NAME}:${params.FRONTEND_IMAGE_TAG}"
                }
            }
        }
    }
    
    post {
        always {
            // Clean up any remaining containers
            sh "docker rm -f flask_backend_container flask_frontend_container || true"
            // Clean up Docker images if needed (optional)
            // sh "docker image prune -f"
        }
    }
}