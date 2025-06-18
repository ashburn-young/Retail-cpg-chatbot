"""
Test utilities for the Retail & CPG Customer Service Chatbot
====================================        elif "track" in message_lower and "order" in message_lower:
            intent = "track_order"
            confidence = 0.9
            # Extract order number pattern
            import re

            order_match = re.search(r"[A-Z]{2}\d+", message)
            if order_match:
                entities["order_number"] = [order_match.group()]===============

This module provides test-specific utilities and app factory functions
that don't trigger the full async lifespan during test collection.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import Settings


def create_test_app():
    """
    Create a FastAPI app instance for testing without async lifespan.

    This function creates a minimal FastAPI application suitable for testing
    without triggering the async initialization that happens in the main app.
    """
    # Set test environment variables
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("API_KEY", "test-api-key")
    os.environ.setdefault("DEBUG", "true")

    # Create FastAPI app without lifespan
    app = FastAPI(
        title="Retail & CPG Customer Service Chatbot (Test)",
        description="Test instance of the chatbot",
        version="1.0.0-test",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Add basic health endpoint for testing
    @app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "test"}

    # Add root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Retail & CPG Customer Service Chatbot API",
            "version": "1.0.0-test",
            "status": "running",
        }

    # Add basic chat endpoint for testing
    @app.post("/chat")
    async def chat(request: dict):
        # Use the MockNLUProcessor for realistic intent classification
        mock_nlu = MockNLUProcessor(get_test_settings())
        result = await mock_nlu.process(request.get("message", ""))

        return {
            "response": f"Response for: {request.get('message', '')}",
            "confidence": result["confidence"],
            "intent": result["intent"],
            "session_id": request.get("session_id", "test_session"),
        }

    return app


def get_test_settings():
    """Get settings configured for testing."""
    os.environ.setdefault("ENVIRONMENT", "test")
    os.environ.setdefault("API_KEY", "test-api-key")
    os.environ.setdefault("DEBUG", "true")

    return Settings()


# Mock classes for testing that don't require complex initialization
class MockNLUProcessor:
    """Mock NLU processor for testing"""

    def __init__(self, settings):
        self.settings = settings

    async def initialize(self):
        pass

    async def process(self, message: str):
        # Simple intent mapping for testing
        message_lower = message.lower()
        intent = "unknown"
        entities = {}
        confidence = 0.5  # Default low confidence

        if "track" in message_lower and "order" in message_lower:
            intent = "track_order"
            confidence = 0.9
            # Extract order number pattern - more flexible patterns
            import re

            # Look for patterns like AB12345678, AB123456, etc.
            order_patterns = [
                r"[A-Z]{2}\d{6,8}",  # AB12345678
                r"[A-Z]{2}\d+",  # AB123, AB12345
                r"\b[A-Z]+\d+\b",  # More general alphanumeric
            ]

            for pattern in order_patterns:
                order_match = re.search(pattern, message)
                if order_match:
                    entities["order_number"] = [order_match.group()]
                    break
        elif "price" in message_lower or "pricing" in message_lower:
            intent = "pricing"
            confidence = 0.9
            # Extract product names
            if "iphone" in message_lower:
                entities["products"] = ["iPhone"]
            # Extract prices with various patterns
            import re

            price_patterns = [
                r"\$(\d+)",  # $500
                r"under \$(\d+)",  # under $500
                r"below \$(\d+)",  # below $500
            ]
            for pattern in price_patterns:
                price_match = re.search(pattern, message_lower)
                if price_match:
                    entities["prices"] = [f"${price_match.group(1)}"]
                    break
        elif (
            "stock" in message_lower
            or "available" in message_lower
            or "availability" in message_lower
            or "check" in message_lower
        ):
            intent = "inventory_check"
            confidence = 0.9
            # Extract product names - enhanced detection
            if "iphone" in message_lower:
                if "13" in message_lower:
                    entities["products"] = ["iPhone 13"]
                else:
                    entities["products"] = ["iPhone"]
            elif "macbook" in message_lower:
                entities["products"] = ["MacBook"]
            elif "product" in message_lower:
                entities["products"] = ["product"]
        elif "store" in message_lower or "find" in message_lower:
            intent = "store_locator"
            confidence = 0.9
            # Extract location info - enhanced detection
            import re

            zip_patterns = [
                r"\b\d{5}\b",  # 90210
                r"in (\d{5})",  # in 90210
            ]
            for pattern in zip_patterns:
                zip_match = re.search(pattern, message)
                if zip_match:
                    if pattern.startswith(r"in"):
                        entities["locations"] = [zip_match.group(1)]
                    else:
                        entities["locations"] = [zip_match.group()]
                    break
        elif "complaint" in message_lower:
            intent = "complaint"
            confidence = 0.8
        elif "account" in message_lower and "help" in message_lower:
            intent = "account_help"
            confidence = 0.8
        elif "under" in message_lower and ("$" in message or "price" in message_lower):
            intent = "pricing"
            confidence = 0.8
            # Extract price info
            import re

            price_match = re.search(r"\$(\d+)", message)
            if price_match:
                entities["prices"] = [f"${price_match.group(1)}"]
        elif "price" in message_lower and "$" in message:
            intent = "pricing"
            confidence = 0.8
            # Extract price info
            import re

            price_match = re.search(r"\$(\d+)", message)
            if price_match:
                entities["prices"] = [f"${price_match.group(1)}"]

        # Handle ambiguous or unclear messages with lower confidence
        if intent == "unknown":
            confidence = 0.3
        elif len(message.split()) < 3:  # Very short messages
            confidence *= 0.7

        return {
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
            "message": message,
        }


class MockResponseGenerator:
    """Mock response generator for testing"""

    def __init__(self, settings):
        self.settings = settings

    async def generate_response(
        self, intent, entities, context, backend_data, confidence=0.9
    ):
        escalate = False

        # Handle escalation logic
        if intent == "complaint":
            escalate = True
        elif confidence < 0.5:  # Low confidence should escalate
            escalate = True

        return {
            "response": f"Mock response for intent: {intent}",
            "confidence": confidence,
            "escalate_to_human": escalate,
        }


class MockContextManager:
    """Mock context manager for testing"""

    def __init__(self, settings):
        self.settings = settings
        self.contexts = {}

    async def initialize(self):
        pass

    async def get_context(self, session_id):
        if session_id not in self.contexts:
            self.contexts[session_id] = {
                "session_id": session_id,
                "messages": [],
                "turn_count": 0,
                "last_intent": None,
                "customer_id": None,
            }
        return self.contexts[session_id]

    async def update_context(self, session_id, updates=None, **kwargs):
        context = await self.get_context(session_id)

        # Handle updates as dict or kwargs
        if updates:
            context.update(updates)
        if kwargs:
            context.update(kwargs)

        # Handle specific update patterns from tests
        if "user_message" in kwargs:
            context["messages"].append(
                {"role": "user", "message": kwargs["user_message"]}
            )
            context["turn_count"] += 1
        if "bot_response" in kwargs:
            context["messages"].append(
                {"role": "bot", "message": kwargs["bot_response"]}
            )

    async def clear_context(self, session_id):
        if session_id in self.contexts:
            del self.contexts[session_id]
        return True  # Return True to indicate success

    async def cleanup(self):
        pass


class MockBackendIntegrator:
    """Mock backend integrator for testing"""

    def __init__(self, settings):
        self.settings = settings

    async def initialize(self):
        pass

    async def process_request(self, intent, entities, context, customer_id=None):
        base_response = {"success": True, "intent": intent}

        if intent == "track_order":
            base_response["order_info"] = {
                "found": True,
                "status": "shipped",
                "tracking_number": "TRK123456",
            }
        elif intent == "inventory_check":
            base_response["inventory_info"] = {
                "found": True,
                "in_stock": True,
                "quantity": 10,
            }
        elif intent == "product_info":
            base_response["product_info"] = {
                "found": True,
                "name": "Test Product",
                "price": "$99.99",
            }
        else:
            base_response["data"] = f"Mock data for {intent}"

        return base_response

    async def get_health_status(self):
        return {"inventory": "healthy", "orders": "healthy", "products": "healthy"}

    async def cleanup(self):
        pass


class MockAnalyticsLogger:
    """Mock analytics logger for testing"""

    def __init__(self, settings):
        self.settings = settings
        self.logs = []

    async def initialize(self):
        pass

    async def log_interaction(
        self,
        session_id,
        customer_id,
        message,
        intent,
        confidence,
        response,
        response_time=None,
    ):
        self.logs.append(
            {
                "type": "interaction",
                "session_id": session_id,
                "customer_id": customer_id,
                "message": message,
                "intent": intent,
                "confidence": confidence,
                "response": response,
                "response_time": response_time,
            }
        )

    async def log_error(self, session_id, error, message):
        self.logs.append(
            {
                "type": "error",
                "session_id": session_id,
                "error": error,
                "message": message,
            }
        )

    async def get_analytics_summary(self):
        return {
            "total_interactions": len(
                [l for l in self.logs if l["type"] == "interaction"]
            ),
            "total_errors": len([l for l in self.logs if l["type"] == "error"]),
        }

    async def get_summary(self, hours=None):
        """Get analytics summary with optional hours parameter for test compatibility"""
        return await self.get_analytics_summary()

    async def cleanup(self):
        pass
