# Retail & CPG Customer Service Chatbot Template
# ==============================================
# 
# This Makefile provides convenient commands for development, testing, and deployment

.PHONY: help install test clean run docker build deploy monitor lint format

# Default target
help:
	@echo "Retail & CPG Customer Service Chatbot"
	@echo "====================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install dependencies and set up the environment"
	@echo "  test        - Run all tests"
	@echo "  test-unit   - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  clean       - Clean up temporary files"
	@echo "  run         - Run the chatbot locally"
	@echo "  run-dev     - Run in development mode with hot reload"
	@echo "  docker      - Build and run with Docker Compose"
	@echo "  build       - Build Docker image"
	@echo "  deploy      - Run deployment script"
	@echo "  monitor     - Run monitoring script"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black and isort"
	@echo "  security    - Run security checks"
	@echo "  docs        - Generate documentation"

# Installation and setup
install:
	@echo "🚀 Setting up Retail & CPG Chatbot..."
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

# Testing
test:
	@echo "🧪 Running all tests..."
	@python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

test-unit:
	@echo "🔬 Running unit tests..."
	@python -m pytest tests/ -v -k "not integration"

test-integration:
	@echo "🔗 Running integration tests..."
	@python -m pytest tests/ -v -k "integration"

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info

# Running the application
run:
	@echo "🚀 Starting chatbot..."
	@python app.py

run-dev:
	@echo "🛠️ Starting in development mode..."
	@uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# Docker operations
docker:
	@echo "🐳 Starting with Docker Compose..."
	@docker-compose up -d

docker-logs:
	@echo "📋 Showing Docker logs..."
	@docker-compose logs -f

docker-stop:
	@echo "🛑 Stopping Docker containers..."
	@docker-compose down

build:
	@echo "🏗️ Building Docker image..."
	@docker build -t retail-chatbot .

# Deployment
deploy:
	@echo "☁️ Running deployment script..."
	@chmod +x scripts/deploy.sh
	@./scripts/deploy.sh

# Monitoring
monitor:
	@echo "📊 Running monitoring..."
	@chmod +x scripts/monitor.sh
	@./scripts/monitor.sh full

monitor-continuous:
	@echo "⏰ Starting continuous monitoring..."
	@chmod +x scripts/monitor.sh
	@./scripts/monitor.sh continuous

# Code quality
lint:
	@echo "🔍 Running linters..."
	@python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	@python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	@echo "✨ Formatting code..."
	@python -m black .
	@python -m isort .

# Security checks
security:
	@echo "🔒 Running security checks..."
	@python -m bandit -r . -f json -o security-report.json
	@echo "Security report generated: security-report.json"

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@python -c "
import app
from fastapi.openapi.utils import get_openapi
import json

openapi_schema = get_openapi(
    title=app.app.title,
    version=app.app.version,
    description=app.app.description,
    routes=app.app.routes,
)

with open('api-docs.json', 'w') as f:
    json.dump(openapi_schema, f, indent=2)

print('API documentation generated: api-docs.json')
"

# Environment setup for different stages
setup-dev:
	@echo "🛠️ Setting up development environment..."
	@cp .env.template .env
	@echo "CHATBOT_ENVIRONMENT=development" >> .env
	@echo "CHATBOT_DEBUG=true" >> .env

setup-prod:
	@echo "🏭 Setting up production environment..."
	@cp .env.template .env
	@echo "CHATBOT_ENVIRONMENT=production" >> .env
	@echo "CHATBOT_DEBUG=false" >> .env

# Database operations (if using database storage)
db-migrate:
	@echo "🗄️ Running database migrations..."
	@# Add your database migration commands here
	@echo "No migrations configured yet"

db-backup:
	@echo "💾 Creating database backup..."
	@# Add your database backup commands here
	@echo "No backup configured yet"

# Load testing
load-test:
	@echo "⚡ Running load tests..."
	@# Add load testing commands here
	@echo "Load testing not configured yet"

# Update dependencies
update-deps:
	@echo "⬆️ Updating dependencies..."
	@pip install --upgrade -r requirements.txt
	@pip freeze > requirements.lock

# Generate sample data
generate-data:
	@echo "📊 Generating sample data..."
	@python -c "
import json
import random
from datetime import datetime, timedelta

# Generate sample customer interactions
interactions = []
intents = ['order_tracking', 'product_info', 'inventory_check', 'store_locator', 'complaint']

for i in range(100):
    interaction = {
        'session_id': f'session_{i:03d}',
        'timestamp': (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
        'intent': random.choice(intents),
        'confidence': round(random.uniform(0.6, 0.95), 2),
        'response_time_ms': random.randint(50, 500),
        'user_satisfaction': random.choice([1, 2, 3, 4, 5])
    }
    interactions.append(interaction)

with open('data/sample_interactions.json', 'w') as f:
    json.dump(interactions, f, indent=2)

print('Sample data generated: data/sample_interactions.json')
"
