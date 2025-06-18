# Retail & CPG Customer Service Chatbot Template

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-24%20passing-brightgreen.svg)](https://github.com/your-repo/actions)
[![Security](https://img.shields.io/badge/security-scanned-green.svg)](https://github.com/your-repo/security)

A comprehensive AI-powered customer service chatbot template designed specifically for the retail and consumer packaged goods (CPG) industry. This template provides a production-ready foundation for building intelligent customer service solutions that can handle common inquiries, integrate with backend systems, and scale to meet enterprise needs.

## � Recent Updates

### ✅ **Complete Test Suite** (Latest)
- **24 comprehensive tests** covering all major components with 100% pass rate
- Enhanced **mock infrastructure** for reliable testing without external dependencies
- **CI/CD pipeline** with automated security scanning and Docker builds
- **GitHub Actions** integration with Bandit, Safety, and Trivy security scans

### 🔒 **Security Enhancements**
- Updated **CodeQL Action** to v3 (fixing deprecated v2 warnings)
- **Dependency vulnerability scanning** with automated security reports
- **Docker security** improvements with non-root user and health checks
- **SARIF upload** for GitHub Security tab integration

### 🐳 **Docker Improvements**
- **Enhanced Dockerfile** with proper package installation and security
- **Robust container testing** with health check verification
- **Better error handling** and logging for containerized deployments
- **Production-ready** multi-stage build process

### 🧪 **Testing Infrastructure**
- **Comprehensive mock classes** for NLU, response generation, context management
- **Realistic entity extraction** with flexible regex patterns for orders, products, prices
- **Advanced intent classification** with confidence scoring and escalation logic
- **Backend integration testing** with order tracking, inventory, and analytics

## �🌟 Features

### Core Capabilities
- **Natural Language Understanding (NLU)** - Intent classification and entity extraction using spaCy
- **Dynamic Response Generation** - Template-based responses with context awareness
- **Conversation Context Management** - Multi-turn conversation tracking with session management
- **Backend System Integration** - Seamless integration with ERP, inventory, and order management systems
- **Intelligent Escalation** - Automatic escalation to human agents based on confidence and complexity
- **Comprehensive Analytics** - Detailed logging and analytics for continuous improvement

### Retail & CPG Specific Features
- **Order Tracking** - Real-time order status and shipment tracking
- **Inventory Management** - Stock availability checks and restock notifications
- **Product Information** - Detailed product specifications, pricing, and availability
- **Store Locator** - Find nearby stores with hours and contact information
- **Customer Support** - Handle complaints, returns, and account assistance
- **Multi-channel Support** - Web, mobile, and API integration ready

### Technical Highlights
- **Async/Await Architecture** - High-performance asynchronous processing
- **Microservices Ready** - Modular design for containerized deployment
- **Cloud Native** - Built for AWS, Azure, and Google Cloud platforms
- **Security First** - JWT authentication, API key management, and HTTPS support
- **Scalable Storage** - Support for Redis, PostgreSQL, and cloud databases
- **Monitoring Ready** - Built-in metrics, health checks, and observability

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd retail-cpg-chatbot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # For full functionality with all optional features
   pip install -r requirements.txt
   
   # OR for minimal setup (CI/CD, basic functionality)
   pip install -r requirements-minimal.txt
   ```

4. **Download the spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up environment variables**
   ```bash
   cp .env.template .env
   # Edit .env file with your configuration
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The chatbot will be available at `http://localhost:8000` with interactive API documentation at `http://localhost:8000/docs`.

### Docker Quick Start

1. **Using Docker Compose (Recommended)**
   ```bash
   docker-compose up -d
   ```
   This starts the chatbot with Redis for context storage and includes health checks.

2. **Using Docker only**
   ```bash
   # Build the image
   docker build -t retail-chatbot .
   
   # Run with health monitoring
   docker run -p 8000:8000 --name chatbot retail-chatbot
   
   # Check health status
   curl http://localhost:8000/health
   ```

3. **Docker Features**
   - **Security**: Runs as non-root user for enhanced security
   - **Health Checks**: Built-in health monitoring with `/health` endpoint
   - **Optimized**: Multi-stage builds for production deployment
   - **Logging**: Structured logging for container environments

## 📖 Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │  Mobile App     │    │   API Client    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
          ┌─────────────────────────────────────────────────┐
          │              FastAPI Gateway                    │
          └─────────────────────┬───────────────────────────┘
                                │
    ┌───────────────────────────────────────────────────────────┐
    │                 Core Chatbot Engine                       │
    ├─────────────┬─────────────┬─────────────┬─────────────────┤
    │ NLU Module  │ Response    │ Context     │ Analytics       │
    │             │ Generator   │ Manager     │ Logger          │
    └─────────────┴─────────────┴─────────────┴─────────────────┘
                                │
    ┌───────────────────────────────────────────────────────────┐
    │              Backend Integration Layer                    │
    ├─────────────┬─────────────┬─────────────┬─────────────────┤
    │ Order API   │ Inventory   │ Product API │ Store Locator   │
    │             │ API         │             │ API             │
    └─────────────┴─────────────┴─────────────┴─────────────────┘
```

### Module Structure

```
retail-cpg-chatbot/
├── app.py                      # Main FastAPI application
├── modules/                    # Core modules
│   ├── nlu.py                 # Natural Language Understanding
│   ├── response.py            # Response generation
│   ├── context.py             # Context management
│   ├── integration.py         # Backend integrations
│   └── analytics.py           # Analytics and logging
├── config/                    # Configuration management
│   └── settings.py           # Settings and environment variables
├── tests/                     # Test suite
│   └── test_app.py           # Comprehensive tests
├── data/                      # Data files and analytics
├── requirements.txt           # Python dependencies
├── Dockerfile                # Container configuration
├── docker-compose.yml        # Multi-service deployment
└── README.md                 # This file
```

## 🛠️ Configuration

### Environment Variables

The chatbot uses environment variables for configuration. Copy `.env.template` to `.env` and customize:

#### Essential Settings
```bash
# Application
CHATBOT_ENVIRONMENT=development
CHATBOT_API_KEY=your-secure-api-key
CHATBOT_COMPANY_NAME=Your Retail Company

# NLU Configuration
CHATBOT_CONFIDENCE_THRESHOLD=0.7
CHATBOT_NLU_MODEL_PATH=en_core_web_sm

# Backend APIs
CHATBOT_ORDER_API_BASE_URL=https://your-order-api.com
CHATBOT_ORDER_API_KEY=your-order-api-key
```

#### Storage Configuration
```bash
# Context Storage
CHATBOT_CONTEXT_STORAGE_TYPE=redis  # or memory
CHATBOT_REDIS_URL=redis://localhost:6379

# Analytics Storage  
CHATBOT_ANALYTICS_ENABLED=true
CHATBOT_ANALYTICS_STORAGE_TYPE=file  # or database
```

### Company Branding

Customize the chatbot for your brand:

```bash
CHATBOT_COMPANY_NAME=Your Retail Company
CHATBOT_SUPPORT_EMAIL=support@yourcompany.com
CHATBOT_SUPPORT_PHONE=1-800-YOUR-HELP
CHATBOT_BRAND_COLOR=#007bff
CHATBOT_LOGO_URL=https://yourcompany.com/logo.png
```

## 🤖 Usage Examples

### Basic Chat Interaction

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to track my order AB12345678",
    "customer_id": "customer_123"
  }'
```

Response:
```json
{
  "response": "I'll help you track your order AB12345678. Your order is currently shipped and expected to arrive tomorrow.",
  "session_id": "session_uuid",
  "intent": "track_order",
  "confidence": 0.95,
  "escalate_to_human": false,
  "suggested_actions": ["check_delivery_address", "contact_shipping_carrier"]
}
```

### Python SDK Example

```python
import asyncio
import aiohttp

async def chat_with_bot():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/chat",
            headers={"Authorization": "Bearer your-api-key"},
            json={"message": "What's the price of iPhone 13?"}
        ) as response:
            result = await response.json()
            print(f"Bot: {result['response']}")

asyncio.run(chat_with_bot())
```

### JavaScript/Node.js Example

```javascript
const response = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your-api-key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Is the MacBook Pro in stock?',
    session_id: 'user-session-123'
  })
});

const data = await response.json();
console.log('Bot response:', data.response);
```

## 🔧 Customization Guide

### Adding New Intents

1. **Update Intent Patterns** in `config/settings.py`:
   ```python
   INTENT_PATTERNS: Dict[str, List[str]] = {
       "your_new_intent": [
           "custom pattern 1",
           "custom pattern 2"
       ]
   }
   ```

2. **Add Response Templates** in `modules/response.py`:
   ```python
   "your_new_intent": [
       "Response template for your new intent: {placeholder}"
   ]
   ```

3. **Implement Handler** in `modules/response.py`:
   ```python
   async def _handle_your_new_intent(self, entities, context, backend_data):
       # Your custom logic here
       return {"response": "Custom response"}
   ```

### Backend Integration

1. **Create Service Class** in `modules/integration.py`:
   ```python
   class YourCustomService(BaseService):
       async def your_method(self, params):
           endpoint = "/your-endpoint"
           return await self._make_request("GET", endpoint, params)
   ```

2. **Register Service** in `BackendIntegrator`:
   ```python
   self.services["your_service"] = YourCustomService(
       self.settings.YOUR_API_BASE_URL,
       self.settings.YOUR_API_KEY
   )
   ```

### Custom Response Templates

Edit the response templates in `config/settings.py`:

```python
RESPONSE_TEMPLATES: Dict[str, str] = {
    "greeting": "Welcome to {company_name}! How can I help you today?",
    "custom_response": "Your custom message with {dynamic_content}"
}
```

## 🧪 Testing

### Comprehensive Test Suite

The chatbot includes a robust testing infrastructure with 24+ test cases covering all major components:

- **API Endpoint Tests** - Health checks, authentication, chat endpoints
- **NLU Processing Tests** - Intent classification, entity extraction, confidence scoring  
- **Response Generation Tests** - Intent-based responses, escalation logic
- **Context Management Tests** - Session creation, updates, cleanup
- **Backend Integration Tests** - Order tracking, inventory checks, product info
- **Analytics Tests** - Interaction logging, error tracking, summary generation
- **Performance Tests** - Concurrent requests, response times
- **Security Tests** - Bandit static analysis, dependency vulnerability scanning

### Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test categories
pytest tests/test_app.py::TestNLU -v                    # NLU tests
pytest tests/test_app.py::TestAPI -v                    # API tests  
pytest tests/test_app.py::TestResponseGeneration -v     # Response tests

# Run with coverage reporting
pytest tests/ --cov=modules --cov-report=html --cov-report=term

# Run security checks
bandit -r modules/ -f json -o bandit-report.json
safety check --json
```

### Test Infrastructure

The project includes sophisticated test utilities in `test_utils.py`:

- **MockNLUProcessor** - Realistic intent classification and entity extraction
- **MockResponseGenerator** - Response generation with escalation logic
- **MockContextManager** - Session and context management testing
- **MockBackendIntegrator** - Backend service simulation
- **MockAnalyticsLogger** - Analytics and logging testing
- **Test App Factory** - Isolated FastAPI app for testing

### CI/CD Pipeline

All tests run automatically in GitHub Actions:

```yaml
# .github/workflows/ci-cd.yml provides:
- Python 3.11 testing environment
- Dependency security scanning (Safety, Bandit)
- Code formatting validation (Black, isort)
- Docker image building and testing
- Security vulnerability scanning (Trivy)
- Automated deployment on success
```

### Testing Individual Components

```bash
# Test NLU module
python modules/nlu.py

# Test response generation
python modules/response.py

# Test backend integration
python modules/integration.py
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:8000
```

## 🚀 Deployment

### Docker Deployment

1. **Build and Deploy**
   ```bash
   docker-compose up -d --build
   ```

2. **Scale Services**
   ```bash
   docker-compose up -d --scale chatbot=3
   ```

### Cloud Deployment

#### AWS Deployment

1. **Using AWS ECS**
   ```bash
   # Build and push to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
   
   docker build -t retail-chatbot .
   docker tag retail-chatbot:latest your-account.dkr.ecr.us-east-1.amazonaws.com/retail-chatbot:latest
   docker push your-account.dkr.ecr.us-east-1.amazonaws.com/retail-chatbot:latest
   ```

2. **Environment Variables for AWS**
   ```bash
   CHATBOT_CONTEXT_STORAGE_TYPE=redis
   CHATBOT_REDIS_URL=your-elasticache-redis-url
   CHATBOT_DATABASE_URL=your-rds-postgresql-url
   ```

#### Azure Deployment

1. **Using Azure Container Instances**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name retail-chatbot \
     --image retail-chatbot:latest \
     --ports 8000 \
     --environment-variables CHATBOT_ENVIRONMENT=production
   ```

2. **Using Azure App Service**
   ```bash
   az webapp create \
     --resource-group myResourceGroup \
     --plan myAppServicePlan \
     --name retail-chatbot \
     --deployment-container-image-name retail-chatbot:latest
   ```

#### Google Cloud Platform

1. **Using Cloud Run**
   ```bash
   gcloud run deploy retail-chatbot \
     --image gcr.io/your-project/retail-chatbot \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Kubernetes Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retail-chatbot
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
        - name: CHATBOT_REDIS_URL
          value: "redis://redis-service:6379"
```

### Production Checklist

- [ ] Set `CHATBOT_ENVIRONMENT=production`
- [ ] Configure secure `CHATBOT_API_KEY`
- [ ] Set up Redis/database for context storage
- [ ] Configure backend API endpoints and keys
- [ ] Set up SSL/TLS certificates
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation
- [ ] Configure auto-scaling
- [ ] Set up backup and disaster recovery
- [ ] **✅ Run complete test suite** (`pytest tests/ -v`)
- [ ] **✅ Security scanning** (Bandit, Safety, Trivy)
- [ ] **✅ Docker health checks** working
- [ ] **✅ CI/CD pipeline** passing
- [ ] Perform penetration testing
- [ ] Load test the deployment

## 📊 Monitoring and Analytics

### Built-in Analytics

The chatbot provides comprehensive analytics out of the box:

```bash
# Get analytics summary
curl -H "Authorization: Bearer your-api-key" \
  "http://localhost:8000/analytics/summary?hours=24"
```

### Metrics Available

- **Conversation Metrics**: Total interactions, unique sessions, average turns
- **Performance Metrics**: Response times, confidence scores, escalation rates
- **Intent Analytics**: Popular intents, success rates, improvement opportunities
- **Error Tracking**: Error rates, failure patterns, system health

### Prometheus Integration

Add to your `docker-compose.yml`:

```yaml
prometheus:
  image: prom/prometheus:latest
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Grafana Dashboards

```yaml
grafana:
  image: grafana/grafana:latest
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin123
  volumes:
    - grafana-data:/var/lib/grafana
```

## 🔒 Security Best Practices

### Authentication and Authorization

1. **API Key Management**
   - Use strong, random API keys
   - Rotate keys regularly
   - Store keys securely (environment variables, key vaults)

2. **JWT Token Security**
   - Use strong secret keys
   - Implement token expiration
   - Consider refresh token patterns

### Data Protection

1. **Sensitive Data Handling**
   - Truncate long messages in logs
   - Anonymize customer data
   - Implement data retention policies

2. **HTTPS/TLS**
   ```python
   # Force HTTPS in production
   if settings.ENVIRONMENT == "production":
       app.add_middleware(HTTPSRedirectMiddleware)
   ```

### Security Headers

```python
from fastapi.middleware.security import SecurityHeadersMiddleware

app.add_middleware(
    SecurityHeadersMiddleware,
    csp="default-src 'self'",
    hsts="max-age=31536000; includeSubDomains",
    frame_options="DENY"
)
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. spaCy Model Not Found
```bash
# Solution: Download the English model
python -m spacy download en_core_web_sm
```

#### 2. Redis Connection Error
```bash
# Check Redis status
redis-cli ping

# Verify Redis URL in environment
echo $CHATBOT_REDIS_URL
```

#### 3. Backend API Timeouts
```python
# Increase timeout in settings.py
API_TIMEOUT_SECONDS: int = 30
```

#### 4. High Memory Usage
```bash
# Monitor memory usage
docker stats

# Adjust worker count
CMD ["uvicorn", "app:app", "--workers", "2"]
```

#### 5. GitHub Actions CI/CD Issues
```bash
# Check workflow status
# Common fixes applied:
# - Updated CodeQL Action from v2 to v3
# - Added security-events permissions for SARIF uploads
# - Enhanced Docker build with proper image loading
# - Added continue-on-error for security scans
```

#### 6. Test Failures
```bash
# Run individual test categories
pytest tests/test_app.py::TestNLU -v           # NLU tests
pytest tests/test_app.py::TestAPI -v           # API tests

# Check test infrastructure
python -c "import test_utils; print('✅ Test utils working')"

# Verify mock classes
ENVIRONMENT=test python -c "from test_utils import MockNLUProcessor; print('✅ Mocks working')"
```

### Debug Mode

Enable debug logging:

```bash
CHATBOT_DEBUG=true
CHATBOT_LOG_LEVEL=DEBUG
```

### Health Checks

Monitor system health:

```bash
# Check application health
curl http://localhost:8000/health

# Check component status
curl -H "Authorization: Bearer your-api-key" \
  http://localhost:8000/analytics/summary
```

## 🤝 Contributing

### Development Setup

1. **Fork and clone the repository**
2. **Create a development branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8 mypy
   ```

4. **Run tests before committing**
   ```bash
   pytest tests/
   black modules/ tests/
   flake8 modules/ tests/
   mypy modules/
   ```

### Code Standards

- **Python Style**: Follow PEP 8, use Black for formatting
- **Type Hints**: Use type hints for all function signatures
- **Documentation**: Document all public methods and classes
- **Testing**: Maintain >90% test coverage
- **Async/Await**: Use async/await for all I/O operations

### Submitting Changes

1. **Create a pull request** with detailed description
2. **Ensure all tests pass** in CI/CD pipeline
3. **Update documentation** for new features
4. **Add appropriate labels** and reviewers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

### Getting Help

- **Documentation**: Check this README and inline code documentation
- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and community support

### Commercial Support

For enterprise support, custom development, or consulting services, please contact:

- **Email**: support@yourcompany.com
- **Phone**: 1-800-YOUR-HELP
- **Website**: https://www.yourcompany.com/support

## 🙏 Acknowledgments

- **FastAPI**: For the excellent web framework
- **spaCy**: For natural language processing capabilities
- **Redis**: For high-performance caching and session storage
- **Docker**: For containerization support
- **The Open Source Community**: For the amazing tools and libraries

---

## 📈 Roadmap

### Version 2.0 (Planned)

- [ ] **Multi-language Support** - Support for Spanish, French, German
- [ ] **Voice Integration** - Speech-to-text and text-to-speech
- [ ] **Machine Learning** - Custom ML models for intent classification
- [ ] **Advanced Analytics** - Predictive analytics and customer insights
- [ ] **Omnichannel Support** - SMS, WhatsApp, Slack integration
- [ ] **A/B Testing** - Built-in A/B testing for response optimization

### Version 3.0 (Future)

- [ ] **AI Personalization** - Dynamic personalization based on customer history
- [ ] **Sentiment Analysis** - Real-time sentiment detection and response adaptation
- [ ] **Knowledge Base** - Integrated knowledge base with FAQ management
- [ ] **Visual Recognition** - Image processing for product identification
- [ ] **Advanced Workflows** - Complex multi-step conversation flows

---

**Ready to transform your customer service with AI?** 🚀

Start building your intelligent customer service solution today with this comprehensive chatbot template. Whether you're a startup or enterprise, this template provides the foundation for creating exceptional customer experiences in the retail and CPG industry.

*Happy coding!* 💻✨
