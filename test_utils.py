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
    os.environ.setdefault('ENVIRONMENT', 'test')
    os.environ.setdefault('API_KEY', 'test-api-key') 
    os.environ.setdefault('DEBUG', 'true')
    
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
    
    return app


def get_test_settings():
    """Get settings configured for testing."""
    os.environ.setdefault('ENVIRONMENT', 'test')
    os.environ.setdefault('API_KEY', 'test-api-key')
    os.environ.setdefault('DEBUG', 'true')
    
    return Settings()
