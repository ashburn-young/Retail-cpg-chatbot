#!/bin/bash

# Retail & CPG Chatbot Deployment Script
# ======================================
# This script helps deploy the chatbot to various cloud platforms

set -e

echo "☁️ Chatbot Deployment Helper"
echo "============================"

# Function to deploy to Azure Container Apps
deploy_azure() {
    echo "🔵 Deploying to Azure Container Apps..."
    
    # Check if Azure CLI is installed
    if ! command -v az &> /dev/null; then
        echo "❌ Azure CLI is required but not installed"
        echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Variables (customize these)
    RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-retail-chatbot-rg}"
    CONTAINER_APP_NAME="${AZURE_APP_NAME:-retail-chatbot}"
    ENVIRONMENT_NAME="${AZURE_ENV_NAME:-retail-chatbot-env}"
    LOCATION="${AZURE_LOCATION:-eastus}"
    
    echo "📋 Using configuration:"
    echo "  Resource Group: $RESOURCE_GROUP"
    echo "  App Name: $CONTAINER_APP_NAME"
    echo "  Environment: $ENVIRONMENT_NAME"
    echo "  Location: $LOCATION"
    
    # Login to Azure (if not already logged in)
    if ! az account show &> /dev/null; then
        echo "🔐 Please login to Azure..."
        az login
    fi
    
    # Create resource group
    echo "🏗️ Creating resource group..."
    az group create --name $RESOURCE_GROUP --location $LOCATION
    
    # Create container app environment
    echo "🌍 Creating container app environment..."
    az containerapp env create \
        --name $ENVIRONMENT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION
    
    # Build and deploy container app
    echo "🚀 Building and deploying container app..."
    az containerapp up \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment $ENVIRONMENT_NAME \
        --source . \
        --ingress external \
        --target-port 8000 \
        --env-vars \
            CHATBOT_ENVIRONMENT=production \
            CHATBOT_DEBUG=false
    
    echo "✅ Deployment to Azure completed!"
    echo "🌐 Your chatbot is available at the URL shown above"
}

# Function to deploy to AWS ECS
deploy_aws() {
    echo "🟠 Deploying to AWS ECS..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        echo "❌ AWS CLI is required but not installed"
        echo "Visit: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
        exit 1
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        echo "❌ Docker is required and must be running"
        exit 1
    fi
    
    # Variables (customize these)
    AWS_REGION="${AWS_REGION:-us-east-1}"
    ECR_REPOSITORY="${ECR_REPOSITORY:-retail-chatbot}"
    CLUSTER_NAME="${ECS_CLUSTER:-retail-chatbot-cluster}"
    
    echo "📋 Using configuration:"
    echo "  Region: $AWS_REGION"
    echo "  ECR Repository: $ECR_REPOSITORY"
    echo "  ECS Cluster: $CLUSTER_NAME"
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"
    
    # Create ECR repository
    echo "📦 Creating ECR repository..."
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION || true
    
    # Login to ECR
    echo "🔐 Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI
    
    # Build and push Docker image
    echo "🏗️ Building Docker image..."
    docker build -t $ECR_REPOSITORY .
    docker tag $ECR_REPOSITORY:latest $ECR_URI:latest
    
    echo "📤 Pushing to ECR..."
    docker push $ECR_URI:latest
    
    echo "✅ Image pushed to ECR: $ECR_URI:latest"
    echo "🚀 Next steps:"
    echo "  1. Create an ECS cluster and service"
    echo "  2. Use the image: $ECR_URI:latest"
    echo "  3. Configure environment variables in your task definition"
}

# Function to generate Kubernetes manifests
generate_k8s() {
    echo "☸️ Generating Kubernetes manifests..."
    
    mkdir -p k8s
    
    cat > k8s/deployment.yaml << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retail-chatbot
  labels:
    app: retail-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: retail-chatbot
  template:
    metadata:
      labels:
        app: retail-chatbot
    spec:
      containers:
      - name: chatbot
        image: retail-chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: CHATBOT_ENVIRONMENT
          value: "production"
        - name: CHATBOT_DEBUG
          value: "false"
        - name: CHATBOT_API_KEY
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: retail-chatbot-service
spec:
  selector:
    app: retail-chatbot
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: chatbot-secrets
type: Opaque
data:
  api-key: # Base64 encoded API key
EOF
    
    echo "✅ Kubernetes manifests generated in k8s/ directory"
    echo "📝 Don't forget to:"
    echo "  1. Build and push your Docker image to a registry"
    echo "  2. Update the image name in deployment.yaml"
    echo "  3. Add your base64-encoded API key to the secret"
    echo "  4. Apply with: kubectl apply -f k8s/"
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1) Azure Container Apps"
echo "2) AWS ECS"
echo "3) Generate Kubernetes manifests"
echo "4) Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        deploy_azure
        ;;
    2)
        deploy_aws
        ;;
    3)
        generate_k8s
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
