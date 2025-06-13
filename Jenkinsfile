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
                    // Check if any parameter is empty and ask for input if needed
                    if (!params.MASTER_USERNAME?.trim() ||
                        !params.DB_PASSWORD?.trim() ||
                        !params.DB_ENDPOINT?.trim() ||
                        !params.DB_INSTANCE_NAME?.trim()) {

                        def userInput = input(
                            id: 'userInput', 
                            message: 'Some required parameters are missing. Please provide the following:', 
                            parameters: [
                                string(name: 'MASTER_USERNAME', defaultValue: params.MASTER_USERNAME ?: '', description: 'DB master username'),
                                string(name: 'DB_PASSWORD', defaultValue: params.DB_PASSWORD ?: '', description: 'DB password'),
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
                        // Assign parameters to environment variables for easier use later
                        env.MASTER_USERNAME = params.MASTER_USERNAME
                        env.DB_PASSWORD = params.DB_PASSWORD
                        env.DB_ENDPOINT = params.DB_ENDPOINT
                        env.DB_INSTANCE_NAME = params.DB_INSTANCE_NAME
                    }
                }
            }
        }
        stage('Build our Backend Image') {
            steps {
                dir('/backend') {
                    sh 'ls'
                    // Modify your parameters.py file with the provided environment variables
                    sh """
                        sed -i 's/^master_username = .*/master_username = "\${MASTER_USERNAME}"/' parameters.py
                        sed -i 's/^db_password = .*/db_password = "\${DB_PASSWORD}"/' parameters.py
                        sed -i 's|^endpoint = .*|endpoint = "\${DB_ENDPOINT}"|' parameters.py
                        sed -i 's/^db_instance_name = .*/db_instance_name = "\${DB_INSTANCE_NAME}"/' parameters.py
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
        stage("Test d'acceptance et de verification") {
            steps {
                script {
                    try {
                        // Start container
                        sh "docker run -d -p 5000:5000 --name flask_backend_container ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG}"
                        
                        // Give container time to start
                        sh "sleep 5"
                        
                        // Get container IP
                        def containerIP = sh(
                            script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' flask_backend_container",
                            returnStdout: true
                        ).trim()
                        
                        // Test with curl and check status code
                       def statusCode = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://${containerIP}:5000",
                            returnStdout: true
                        ).trim()
                        
                        // Validate status code (200 is OK)
                        if (statusCode != "200") {
                            error "HTTP request failed with status code: ${statusCode}"
                        } else {
                            echo "HTTP request successful with status code: ${statusCode}"
                        }
                    } finally {
                        // Always clean up the container
                        sh "docker rm -f flask_backend_container || true"
                    }
                }
            }
        }

        stage("Push to Docker Hub") {
            steps {
                // Use Jenkins credentials (create a 'dockerhub-credentials' with your Docker Hub username/password)
                withCredentials([usernamePassword(
                    credentialsId: '550b2578-f31d-4312-adbd-f0714cb4d0fe',
                    usernameVariable: 'DOCKERHUB_USER', 
                    passwordVariable: 'DOCKERHUB_PASS'
                    )]) {
                    sh "echo \"Tagging my image inother to push on docker hub\""
                    sh "docker tag ${params.BACKEND_BUILD_IMAGE}:${params.BACKEND_IMAGE_TAG} ${DOCKERHUB_USER}/${params.DOCKERHUB_BACKEND_REPO_NAME}:${params.BACKEND_IMAGE_TAG}"
                    sh "echo \"Logging in to Docker Hub as ${DOCKERHUB_USER}\""
                    sh "docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASS}"
                    sh "sleep 10"
                    sh "docker push ${DOCKERHUB_USER}/${params.DOCKERHUB_BACKEND_REPO_NAME}:${params.BACKEND_IMAGE_TAG}"
                }
            }
        }
        //stage that handles the frontend image build-------------------------------------------------------------------------------------
       
       stage("Validate frontend parameters"){
           steps{
               script{
                 if (!params.BACKEND_URL.trim()) {
                     def userInput = input(
                        id: 'frontend_input',
                        message: 'The Backend URL is required inother to proceed',
                        parameters: [
                            string(name: 'BACKEND_URL', defaultValue: params.BACKEND_URL? : '' , description: 'Backend url made up of the protocol and host')
                        ]
                     )
                 } else {
                     env.BACKEND_URL = params.BACKEND_URL
                 }
               }
           }
       }

        stage("Build our frontend Image") {
                steps {
                    // switch into your frontend folder
                    dir('/frontend') {
                        // list files (optional sanity check)
                        sh 'ls'  
                        //update the frontend app.py endpoints to reflect the backend url 
                        sh """
                        sed -i "s#http://localhost:5000#http://${BACKEND_URL}#g" app.py
                        """
                        // build with the name and tag from your parameters
                        sh """
                        docker build \
                            -t ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG} \
                            .
                        """
                    }
                }
            }
        
        stage("Test d'acceptance") {
            steps {
                script {
                    try {
                        // Start container
                        sh "docker run -d -p 4000:4000 --name flask_frontend_container ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG}"
                        
                        // Give container time to start
                        sh "sleep 5"
                        
                        // Get container IP
                        def containerIP = sh(
                            script: "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' flask_frontend_container",
                            returnStdout: true
                        ).trim()
                        
                        // Test with curl and check status code
                       def statusCode = sh(
                            script: "curl -s -o /dev/null -w '%{http_code}' http://${containerIP}:4000",
                            returnStdout: true
                        ).trim()
                        
                        // Validate status code (200 is OK)
                        if (statusCode != "200") {
                            error "HTTP request failed with status code: ${statusCode}"
                        } else {
                            echo "HTTP request successful with status code: ${statusCode}"
                        }
                    } finally {
                        // Always clean up the container
                        sh "docker rm -f flask_frontend_container || true"
                    }
                }
            }
        }
        stage("Push to Docker Hub") {
        steps {
            // Use Jenkins credentials (create a 'dockerhub-credentials' with your Docker Hub username/password)
            withCredentials([usernamePassword(
                credentialsId: '550b2578-f31d-4312-adbd-f0714cb4d0fe',
                usernameVariable: 'DOCKERHUB_USER', 
                passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                sh "echo \"Tagging my image inother to push on docker hub\""
                sh "docker tag ${params.FRONTEND_BUILD_IMAGE}:${params.FRONTEND_IMAGE_TAG} ${DOCKERHUB_USER}/${params.DOCKERHUB_FRONTEND_REPO_NAME}:latest"
                sh "echo \"Logging in to Docker Hub as ${DOCKERHUB_USER}\""
                sh "docker login -u ${DOCKERHUB_USER} -p ${DOCKERHUB_PASS}"
                sh "sleep 10"
                sh "docker push ${DOCKERHUB_USER}/${params.DOCKERHUB_FRONTEND_REPO_NAME}:latest"
            }
        }
    }
    }
}

