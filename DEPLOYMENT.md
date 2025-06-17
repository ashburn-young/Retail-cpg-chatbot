# 🚀 Deployment Guide for Retail & CPG Customer Service Chatbot

This guide provides comprehensive instructions for deploying the chatbot template to various cloud platforms and environments.

## 📋 Pre-Deployment Checklist

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] Docker and Docker Compose installed
- [ ] Git repository set up
- [ ] Cloud platform account (AWS/Azure/GCP)
- [ ] Domain name (optional, for production)
- [ ] SSL certificate (for HTTPS)

### Environment Setup
- [ ] Environment variables configured
- [ ] API keys and secrets prepared
- [ ] Database/Redis connection strings ready
- [ ] Monitoring tools configured
- [ ] CI/CD pipeline set up (optional)

## 🏠 Local Development Deployment

### Quick Start
```bash
# Clone and setup
git clone <your-repo-url>
cd retail-cpg-chatbot

# Automated setup
make install

# Run locally
make run
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Configure environment
cp .env.template .env
# Edit .env with your settings

# Run the application
python app.py
```

### Docker Development
```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t retail-chatbot .
docker run -p 8000:8000 retail-chatbot
```

## ☁️ Cloud Deployment Options

### 1. Azure Container Apps (Recommended)

#### Prerequisites
- Azure CLI installed and configured
- Azure subscription with appropriate permissions

#### Automated Deployment
```bash
# Set environment variables
export AZURE_RESOURCE_GROUP="retail-chatbot-rg"
export AZURE_APP_NAME="retail-chatbot"
export AZURE_ENV_NAME="retail-chatbot-env"
export AZURE_LOCATION="eastus"

# Run deployment script
./scripts/deploy.sh
# Choose option 1 (Azure Container Apps)
```

#### Manual Deployment
```bash
# Login to Azure
az login

# Create resource group
az group create --name retail-chatbot-rg --location eastus

# Create container app environment
az containerapp env create \
  --name retail-chatbot-env \
  --resource-group retail-chatbot-rg \
  --location eastus

# Deploy the application
az containerapp up \
  --name retail-chatbot \
  --resource-group retail-chatbot-rg \
  --environment retail-chatbot-env \
  --source . \
  --ingress external \
  --target-port 8000 \
  --env-vars \
    CHATBOT_ENVIRONMENT=production \
    CHATBOT_DEBUG=false \
    CHATBOT_API_KEY=your-api-key-here
```

#### Configure Azure Services
```bash
# Add Redis cache
az redis create \
  --name retail-chatbot-redis \
  --resource-group retail-chatbot-rg \
  --location eastus \
  --sku Basic \
  --vm-size c0

# Update container app with Redis connection
az containerapp update \
  --name retail-chatbot \
  --resource-group retail-chatbot-rg \
  --set-env-vars CHATBOT_REDIS_URL="redis://your-redis-url:6379"
```

### 2. AWS ECS

#### Prerequisites
- AWS CLI installed and configured
- Docker installed
- ECR repository permissions

#### Automated Deployment
```bash
# Set environment variables
export AWS_REGION="us-east-1"
export ECR_REPOSITORY="retail-chatbot"
export ECS_CLUSTER="retail-chatbot-cluster"

# Run deployment script
./scripts/deploy.sh
# Choose option 2 (AWS ECS)
```

#### Manual Deployment
```bash
# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/retail-chatbot"

# Create ECR repository
aws ecr create-repository --repository-name retail-chatbot --region us-east-1

# Build and push image
docker build -t retail-chatbot .
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_URI
docker tag retail-chatbot:latest $ECR_URI:latest
docker push $ECR_URI:latest

# Create ECS cluster
aws ecs create-cluster --cluster-name retail-chatbot-cluster

# Create task definition (see aws-task-definition.json)
aws ecs register-task-definition --cli-input-json file://aws-task-definition.json

# Create service
aws ecs create-service \
  --cluster retail-chatbot-cluster \
  --service-name retail-chatbot-service \
  --task-definition retail-chatbot-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### 3. Kubernetes (Any Cloud)

#### Generate Kubernetes Manifests
```bash
# Generate manifests
./scripts/deploy.sh
# Choose option 3 (Generate Kubernetes manifests)

# Or manually create them
mkdir -p k8s
```

#### Deploy to Kubernetes
```bash
# Build and push image to your registry
docker build -t your-registry/retail-chatbot:latest .
docker push your-registry/retail-chatbot:latest

# Update image in k8s/deployment.yaml
# Add your API key to k8s/deployment.yaml secrets

# Deploy to cluster
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=retail-chatbot
kubectl get services
```

#### Helm Chart (Advanced)
```bash
# Create Helm chart
helm create retail-chatbot-chart

# Customize values.yaml with your configuration
# Deploy with Helm
helm install retail-chatbot ./retail-chatbot-chart
```

## 🔧 Production Configuration

### Environment Variables
```bash
# Essential production settings
CHATBOT_ENVIRONMENT=production
CHATBOT_DEBUG=false
CHATBOT_API_KEY=your-secure-api-key
CHATBOT_SECRET_KEY=your-jwt-secret

# Database/Cache
CHATBOT_CONTEXT_STORAGE_TYPE=redis
CHATBOT_REDIS_URL=redis://your-redis-cluster:6379
CHATBOT_DATABASE_URL=postgresql://user:pass@host:5432/dbname

# External integrations
CHATBOT_ORDER_API_URL=https://your-erp-system.com/api
CHATBOT_INVENTORY_API_URL=https://your-inventory-system.com/api
CHATBOT_ORDER_API_KEY=your-order-api-key
CHATBOT_INVENTORY_API_KEY=your-inventory-api-key

# Monitoring
CHATBOT_ANALYTICS_ENABLED=true
CHATBOT_LOG_LEVEL=INFO

# Security
CHATBOT_CORS_ORIGINS=["https://your-frontend.com"]
CHATBOT_RATE_LIMIT_ENABLED=true
CHATBOT_RATE_LIMIT_REQUESTS=100
CHATBOT_RATE_LIMIT_WINDOW=3600
```

### SSL/HTTPS Configuration
```bash
# For container deployments, SSL is typically handled by the load balancer
# For direct deployments, configure SSL certificates:

# Using Let's Encrypt with Certbot
certbot --nginx -d your-domain.com

# Or provide certificate files
CHATBOT_SSL_CERT_FILE=/path/to/cert.pem
CHATBOT_SSL_KEY_FILE=/path/to/key.pem
```

### Database Setup
```sql
-- PostgreSQL setup for analytics (optional)
CREATE DATABASE chatbot_analytics;
CREATE USER chatbot_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE chatbot_analytics TO chatbot_user;

-- Create tables for conversation history
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(100),
    confidence FLOAT,
    response TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_id ON conversations(session_id);
CREATE INDEX idx_timestamp ON conversations(timestamp);
```

## 📊 Monitoring and Observability

### Health Checks
```bash
# Basic health check
curl https://your-chatbot.com/health

# Detailed monitoring
./scripts/monitor.sh full

# Continuous monitoring
./scripts/monitor.sh continuous
```

### Logging Configuration
```yaml
# docker-compose.override.yml for production logging
version: '3.8'
services:
  chatbot:
    volumes:
      - ./logs:/app/logs
    environment:
      - CHATBOT_LOG_LEVEL=INFO
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Prometheus Metrics
```python
# Add to app.py for Prometheus integration
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('chatbot_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('chatbot_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy Chatbot
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m spacy download en_core_web_sm
      - name: Run tests
        run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Azure
        run: |
          # Add your deployment commands here
          echo "Deploying to production..."
```

## 🛡️ Security Best Practices

### 1. Environment Security
```bash
# Use secrets management
# Azure Key Vault
az keyvault secret set --vault-name your-vault --name chatbot-api-key --value your-key

# AWS Secrets Manager
aws secretsmanager create-secret --name chatbot-api-key --secret-string your-key

# Kubernetes secrets
kubectl create secret generic chatbot-secrets --from-literal=api-key=your-key
```

### 2. Network Security
```yaml
# Security groups/firewall rules
# Only allow HTTPS traffic (port 443)
# Restrict database access to application subnet only
# Use private endpoints for cloud services
```

### 3. Application Security
```python
# Enable security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["your-domain.com"])
```

## 🔍 Troubleshooting

### Common Issues

1. **spaCy Model Not Found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **Redis Connection Failed**
   ```bash
   # Check Redis connectivity
   redis-cli -h your-redis-host ping
   ```

3. **High Memory Usage**
   ```bash
   # Adjust container memory limits
   docker run -m 512m retail-chatbot
   ```

4. **API Rate Limiting**
   ```python
   # Increase rate limits in settings
   CHATBOT_RATE_LIMIT_REQUESTS=1000
   ```

### Performance Optimization

1. **Enable Caching**
   ```python
   # Use Redis for response caching
   CHATBOT_RESPONSE_CACHE_ENABLED=true
   CHATBOT_RESPONSE_CACHE_TTL=3600
   ```

2. **Database Optimization**
   ```sql
   -- Add database indexes
   CREATE INDEX CONCURRENTLY idx_conversations_intent ON conversations(intent);
   ```

3. **Container Optimization**
   ```dockerfile
   # Multi-stage build for smaller images
   FROM python:3.11-slim as builder
   # ... build steps ...
   
   FROM python:3.11-slim
   COPY --from=builder /app /app
   ```

## 📈 Scaling Considerations

### Horizontal Scaling
```yaml
# Kubernetes horizontal pod autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: retail-chatbot-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: retail-chatbot
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Load Balancing
```bash
# Azure Application Gateway
az network application-gateway create \
  --name chatbot-gateway \
  --resource-group retail-chatbot-rg \
  --capacity 2 \
  --sku Standard_v2

# AWS Application Load Balancer
aws elbv2 create-load-balancer \
  --name chatbot-alb \
  --type application \
  --scheme internet-facing
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks
- [ ] Update dependencies monthly
- [ ] Review logs weekly
- [ ] Monitor performance metrics
- [ ] Backup conversation data
- [ ] Update NLU training data
- [ ] Security patches and updates

### Monitoring Checklist
- [ ] Application health status
- [ ] Response times under 500ms
- [ ] Error rate under 1%
- [ ] Memory usage under 80%
- [ ] CPU usage under 70%
- [ ] Database connection pool healthy

For additional support, refer to the main README.md or contact your development team.
