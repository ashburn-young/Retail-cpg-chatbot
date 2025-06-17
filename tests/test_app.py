"""
Test suite for the Retail & CPG Customer Service Chatbot
========================================================

This module contains comprehensive tests for all chatbot components
including NLU, response generation, context management, and backend integration.
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import the modules to test
from app import app
from modules.nlu import NLUProcessor
from modules.response import ResponseGenerator
from modules.context import ContextManager
from modules.integration import BackendIntegrator
from modules.analytics import AnalyticsLogger
from config.settings import Settings

# Test client
from fastapi.testclient import TestClient

# Test configuration
@pytest.fixture
def test_settings():
    """Test settings configuration"""
    return Settings(
        ENVIRONMENT="test",
        DEBUG=True,
        API_KEY="test-api-key",
        CONFIDENCE_THRESHOLD=0.7,
        CONTEXT_STORAGE_TYPE="memory",
        ANALYTICS_ENABLED=True,
        ANALYTICS_STORAGE_TYPE="file"
    )

@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)

@pytest.fixture
async def nlu_processor(test_settings):
    """Initialize NLU processor for testing"""
    processor = NLUProcessor(test_settings)
    await processor.initialize()
    return processor

@pytest.fixture
async def response_generator(test_settings):
    """Initialize response generator for testing"""
    return ResponseGenerator(test_settings)

@pytest.fixture
async def context_manager(test_settings):
    """Initialize context manager for testing"""
    manager = ContextManager(test_settings)
    await manager.initialize()
    return manager

@pytest.fixture
async def backend_integrator(test_settings):
    """Initialize backend integrator for testing"""
    integrator = BackendIntegrator(test_settings)
    await integrator.initialize()
    return integrator

@pytest.fixture
async def analytics_logger(test_settings):
    """Initialize analytics logger for testing"""
    logger = AnalyticsLogger(test_settings)
    await logger.initialize()
    return logger

# API Tests
class TestAPI:
    """Test the main API endpoints"""
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_check(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
    
    def test_chat_endpoint_unauthorized(self, client):
        """Test chat endpoint without authorization"""
        response = client.post("/chat", json={
            "message": "Hello, I need help"
        })
        assert response.status_code == 401
    
    def test_chat_endpoint_authorized(self, client):
        """Test chat endpoint with authorization"""
        headers = {"Authorization": "Bearer test-api-key"}
        response = client.post("/chat", json={
            "message": "I want to track my order AB12345678"
        }, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "intent" in data
        assert "confidence" in data
        assert "session_id" in data

# NLU Tests
class TestNLU:
    """Test Natural Language Understanding"""
    
    @pytest.mark.asyncio
    async def test_intent_classification(self, nlu_processor):
        """Test intent classification accuracy"""
        test_cases = [
            ("I want to track my order AB123", "track_order"),
            ("What's the price of iPhone?", "pricing"),
            ("Is the product in stock?", "inventory_check"),
            ("Where is your store?", "store_locator"),
            ("I have a complaint", "complaint"),
            ("Help me with my account", "account_help")
        ]
        
        for message, expected_intent in test_cases:
            result = await nlu_processor.process(message)
            assert result["intent"] == expected_intent
            assert result["confidence"] > 0.0
    
    @pytest.mark.asyncio
    async def test_entity_extraction(self, nlu_processor):
        """Test entity extraction"""
        test_cases = [
            ("Track order AB12345678", {"order_number"}),
            ("Check iPhone 13 availability", {"products"}),
            ("Find store in 90210", {"locations"}),
            ("Price under $500", {"prices"})
        ]
        
        for message, expected_entity_types in test_cases:
            result = await nlu_processor.process(message)
            entities = result["entities"]
            
            # Check if any expected entity type is found
            found_types = set(entities.keys())
            assert len(found_types.intersection(expected_entity_types)) > 0
    
    @pytest.mark.asyncio
    async def test_confidence_scoring(self, nlu_processor):
        """Test confidence scoring"""
        # High confidence messages
        high_confidence_messages = [
            "track my order number AB123456",
            "what is the price of iPhone 13",
            "is the MacBook in stock"
        ]
        
        for message in high_confidence_messages:
            result = await nlu_processor.process(message)
            assert result["confidence"] > 0.7
        
        # Low confidence messages (ambiguous)
        low_confidence_messages = [
            "hello",
            "maybe",
            "xyz abc def"
        ]
        
        for message in low_confidence_messages:
            result = await nlu_processor.process(message)
            assert result["confidence"] < 0.8

# Response Generation Tests
class TestResponseGeneration:
    """Test response generation logic"""
    
    @pytest.mark.asyncio
    async def test_intent_based_responses(self, response_generator):
        """Test responses for different intents"""
        test_cases = [
            {
                "intent": "track_order",
                "entities": {"order_number": ["AB123"]},
                "context": {},
                "backend_data": {
                    "order_info": {
                        "found": True,
                        "order_number": "AB123",
                        "status": "shipped",
                        "additional_info": "Arriving tomorrow"
                    }
                }
            },
            {
                "intent": "product_info",
                "entities": {"products": ["iPhone"]},
                "context": {},
                "backend_data": {
                    "product_info": {
                        "found": True,
                        "name": "iPhone",
                        "details": "Latest smartphone"
                    }
                }
            }
        ]
        
        for test_case in test_cases:
            response = await response_generator.generate_response(
                intent=test_case["intent"],
                entities=test_case["entities"],
                context=test_case["context"],
                backend_data=test_case["backend_data"]
            )
            
            assert "response" in response
            assert len(response["response"]) > 0
            assert isinstance(response.get("escalate_to_human"), bool)
    
    @pytest.mark.asyncio
    async def test_escalation_logic(self, response_generator):
        """Test escalation logic"""
        # Test complaint escalation
        complaint_response = await response_generator.generate_response(
            intent="complaint",
            entities={},
            context={},
            backend_data={}
        )
        
        assert complaint_response.get("escalate_to_human") == True
        
        # Test low confidence escalation
        low_confidence_response = await response_generator.generate_response(
            intent="general_inquiry",
            entities={},
            context={},
            backend_data={},
            confidence=0.3
        )
        
        assert low_confidence_response.get("escalate_to_human") == True

# Context Management Tests
class TestContextManagement:
    """Test conversation context management"""
    
    @pytest.mark.asyncio
    async def test_context_creation(self, context_manager):
        """Test context creation for new sessions"""
        session_id = "test_session_123"
        context = await context_manager.get_context(session_id)
        
        assert context["session_id"] == session_id
        assert "turn_count" in context
        assert context["turn_count"] == 0
    
    @pytest.mark.asyncio
    async def test_context_updates(self, context_manager):
        """Test context updates"""
        session_id = "test_session_456"
        
        # Initial context
        await context_manager.get_context(session_id)
        
        # Update context
        await context_manager.update_context(
            session_id,
            {
                "customer_id": "customer_123",
                "last_intent": "track_order",
                "last_entities": {"order_number": ["AB123"]}
            },
            user_message="Track my order",
            bot_response="I'll help you track your order"
        )
        
        # Verify updates
        updated_context = await context_manager.get_context(session_id)
        assert updated_context["customer_id"] == "customer_123"
        assert updated_context["last_intent"] == "track_order"
        assert updated_context["turn_count"] == 1
    
    @pytest.mark.asyncio
    async def test_context_cleanup(self, context_manager):
        """Test context cleanup"""
        session_id = "test_session_789"
        
        # Create context
        await context_manager.get_context(session_id)
        
        # Clear context
        result = await context_manager.clear_context(session_id)
        assert result == True

# Backend Integration Tests
class TestBackendIntegration:
    """Test backend system integration"""
    
    @pytest.mark.asyncio
    async def test_order_tracking(self, backend_integrator):
        """Test order tracking integration"""
        result = await backend_integrator.process_request(
            "track_order",
            {"order_number": ["AB12345678"]},
            {},
            "customer_123"
        )
        
        assert "order_info" in result
        order_info = result["order_info"]
        assert "found" in order_info
    
    @pytest.mark.asyncio
    async def test_inventory_check(self, backend_integrator):
        """Test inventory check integration"""
        result = await backend_integrator.process_request(
            "inventory_check",
            {"products": ["iPhone 13"]},
            {}
        )
        
        assert "inventory_info" in result
        inventory_info = result["inventory_info"]
        assert "in_stock" in inventory_info
    
    @pytest.mark.asyncio
    async def test_product_info(self, backend_integrator):
        """Test product information integration"""
        result = await backend_integrator.process_request(
            "product_info",
            {"products": ["iPhone 13"]},
            {}
        )
        
        assert "product_info" in result
        product_info = result["product_info"]
        assert "found" in product_info
    
    @pytest.mark.asyncio
    async def test_service_health(self, backend_integrator):
        """Test service health checks"""
        health_status = await backend_integrator.get_health_status()
        
        assert isinstance(health_status, dict)
        assert len(health_status) > 0
        
        for service_name, status in health_status.items():
            assert status in ["healthy", "degraded", "unavailable"]

# Analytics Tests
class TestAnalytics:
    """Test analytics and logging"""
    
    @pytest.mark.asyncio
    async def test_interaction_logging(self, analytics_logger):
        """Test interaction logging"""
        await analytics_logger.log_interaction(
            session_id="test_session",
            customer_id="customer_123",
            message="Test message",
            intent="test_intent",
            confidence=0.9,
            response="Test response",
            response_time=0.5
        )
        
        # Verify logging succeeded (no exceptions)
        assert True
    
    @pytest.mark.asyncio
    async def test_error_logging(self, analytics_logger):
        """Test error logging"""
        await analytics_logger.log_error(
            session_id="test_session",
            error="Test error",
            message="Test message"
        )
        
        # Verify logging succeeded (no exceptions)
        assert True
    
    @pytest.mark.asyncio
    async def test_analytics_summary(self, analytics_logger):
        """Test analytics summary generation"""
        # Log some test interactions first
        for i in range(3):
            await analytics_logger.log_interaction(
                session_id=f"test_session_{i}",
                customer_id=f"customer_{i}",
                message=f"Test message {i}",
                intent="test_intent",
                confidence=0.8,
                response=f"Test response {i}"
            )
        
        # Get summary
        summary = await analytics_logger.get_summary(hours=1)
        
        assert "total_interactions" in summary
        assert summary["total_interactions"] >= 3

# Integration Tests
class TestFullIntegration:
    """Test full end-to-end integration"""
    
    @pytest.mark.asyncio
    async def test_complete_conversation_flow(self, client):
        """Test complete conversation flow"""
        headers = {"Authorization": "Bearer test-api-key"}
        
        # First message
        response1 = client.post("/chat", json={
            "message": "Hello, I need help"
        }, headers=headers)
        
        assert response1.status_code == 200
        data1 = response1.json()
        session_id = data1["session_id"]
        
        # Follow-up message with same session
        response2 = client.post("/chat", json={
            "message": "I want to track my order AB12345678",
            "session_id": session_id
        }, headers=headers)
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["session_id"] == session_id
        assert data2["intent"] == "track_order"

# Performance Tests
class TestPerformance:
    """Test performance and load handling"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, client):
        """Test handling concurrent requests"""
        headers = {"Authorization": "Bearer test-api-key"}
        
        async def make_request(i):
            response = client.post("/chat", json={
                "message": f"Test message {i}"
            }, headers=headers)
            return response.status_code
        
        # Make 10 concurrent requests
        tasks = [make_request(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    @pytest.mark.asyncio
    async def test_response_time(self, nlu_processor):
        """Test response time performance"""
        message = "I want to track my order AB12345678"
        
        start_time = datetime.now()
        result = await nlu_processor.process(message)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        # Response should be under 1 second for NLU processing
        assert response_time < 1.0
        assert result["intent"] is not None

# Configuration Tests
class TestConfiguration:
    """Test configuration and settings"""
    
    def test_settings_validation(self):
        """Test settings validation"""
        # Valid settings
        valid_settings = Settings(
            ENVIRONMENT="test",
            CONFIDENCE_THRESHOLD=0.7,
            LOG_LEVEL="INFO"
        )
        
        assert valid_settings.ENVIRONMENT == "test"
        assert valid_settings.CONFIDENCE_THRESHOLD == 0.7
        
        # Invalid confidence threshold
        with pytest.raises(ValueError):
            Settings(CONFIDENCE_THRESHOLD=1.5)
    
    def test_environment_specific_settings(self):
        """Test environment-specific settings"""
        dev_settings = Settings(ENVIRONMENT="development")
        prod_settings = Settings(ENVIRONMENT="production")
        
        assert dev_settings.DEBUG == True
        assert prod_settings.DEBUG == False

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
