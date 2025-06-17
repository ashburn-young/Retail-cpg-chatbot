"""
Retail & CPG Customer Service Chatbot Modules
=============================================

This package contains all the core modules for the chatbot:

- nlu: Natural Language Understanding processing
- response: Response generation and templating  
- context: Conversation context and session management
- integration: Backend system integration
- analytics: Logging and analytics functionality

Each module is designed to be modular and independently testable.
"""

__version__ = "1.0.0"
__author__ = "AI Agent Template"

# Import main classes for easy access
from .nlu import NLUProcessor
from .response import ResponseGenerator  
from .context import ContextManager
from .integration import BackendIntegrator
from .analytics import AnalyticsLogger

__all__ = [
    "NLUProcessor",
    "ResponseGenerator", 
    "ContextManager",
    "BackendIntegrator",
    "AnalyticsLogger"
]
