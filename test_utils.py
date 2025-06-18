"""
Test utilities for the Retail & CPG Customer Service Chatbot
============================================================

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
        # Simple mock response for testing
        return {
            "response": "This is a test response",
            "confidence": 0.9,
            "intent": "test_intent",
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
        return {
            "intent": "test_intent",
            "entities": {},
            "confidence": 0.9,
            "message": message,
        }


class MockResponseGenerator:
    """Mock response generator for testing"""

    def __init__(self, settings):
        self.settings = settings

    async def generate_response(self, intent, entities, context, backend_data):
        return {
            "response": f"Mock response for intent: {intent}",
            "confidence": 0.9,
            "escalate": intent == "complaint",
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
            self.contexts[session_id] = {"session_id": session_id, "messages": []}
        return self.contexts[session_id]

    async def update_context(self, session_id, updates):
        context = await self.get_context(session_id)
        context.update(updates)

    async def cleanup(self):
        pass


class MockBackendIntegrator:
    """Mock backend integrator for testing"""

    def __init__(self, settings):
        self.settings = settings

    async def initialize(self):
        pass

    async def process_request(self, intent, entities, context, customer_id=None):
        return {"success": True, "data": f"Mock data for {intent}", "intent": intent}

    async def get_health_status(self):
        return {"status": "healthy", "services": ["mock"]}

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

    async def cleanup(self):
        pass
