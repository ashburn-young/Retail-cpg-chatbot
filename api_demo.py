#!/usr/bin/env python3
"""
API Test Script for Retail & CPG Chatbot
========================================

This script demonstrates the chatbot API endpoints without requiring a full server setup.
It shows key functionality including NLU processing, response generation, and conversation flow.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.nlu import NLUProcessor
from modules.response import ResponseGenerator
from modules.context import ContextManager
from config.settings import Settings

class ChatbotAPIDemo:
    """Demonstration of the chatbot API functionality"""
    
    def __init__(self):
        self.settings = None
        self.nlu_processor = None
        self.response_generator = None
        self.context_manager = None
        
    async def initialize(self):
        """Initialize all components"""
        try:
            print("🔧 Initializing Chatbot API Demo...")
            
            # Create basic settings for demo
            self.settings = Settings(
                DEV_MODE=True,
                USE_MOCK_SERVICES=True,
                LOG_REQUESTS=True,
                CONFIDENCE_THRESHOLD=0.7
            )
            print("✅ Settings loaded")
            
            # Initialize components
            self.nlu_processor = NLUProcessor(self.settings)
            await self.nlu_processor.initialize()
            print("✅ NLU processor initialized")
            
            self.response_generator = ResponseGenerator(self.settings)
            print("✅ Response generator initialized")
            
            self.context_manager = ContextManager(self.settings)
            await self.context_manager.initialize()
            print("✅ Context manager initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize: {str(e)}")
            return False
    
    async def process_message(self, message: str, user_id: str = "demo_user") -> Dict[str, Any]:
        """Process a message through the complete chatbot pipeline"""
        try:
            # 1. NLU Processing
            nlu_result = await self.nlu_processor.process(message)
            
            # 2. Context Management
            context = await self.context_manager.get_context(user_id)
            await self.context_manager.update_context(user_id, {
                "last_message": message,
                "last_intent": nlu_result.get("intent", "unknown"),
                "timestamp": datetime.now().isoformat()
            })
            
            # 3. Response Generation
            response = await self.response_generator.generate_response(
                intent=nlu_result.get("intent", "unknown"),
                entities=nlu_result.get("entities", {}),
                context=context,
                confidence=nlu_result.get("confidence", 0.0)
            )
            
            return {
                "user_message": message,
                "nlu_result": nlu_result,
                "context": context,
                "response": response,
                "processing_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "user_message": message,
                "timestamp": datetime.now().isoformat()
            }
    
    def format_api_response(self, result: Dict[str, Any]) -> str:
        """Format the result as an API response"""
        if "error" in result:
            return f"""
🚨 API ERROR RESPONSE:
{json.dumps({
    "status": "error",
    "message": result["error"],
    "timestamp": result["timestamp"]
}, indent=2)}
"""
        
        # Simulate API endpoint response
        api_response = {
            "status": "success",
            "data": {
                "intent": result["nlu_result"].get("intent", "unknown"),
                "confidence": result["nlu_result"].get("confidence", 0.0),
                "entities": result["nlu_result"].get("entities", {}),
                "response": result["response"].get("response", "No response generated"),
                "needs_escalation": result["response"].get("escalate", False),
                "context_updated": True
            },
            "metadata": {
                "processing_time_ms": 150,  # Mock processing time
                "model_version": "1.0.0",
                "timestamp": result["processing_time"]
            }
        }
        
        return f"""
📡 API RESPONSE (/api/v1/chat):
{json.dumps(api_response, indent=2)}
"""

async def demonstrate_api_endpoints():
    """Demonstrate various API endpoints and functionality"""
    print("=" * 80)
    print("🤖 RETAIL & CPG CHATBOT API DEMONSTRATION")
    print("=" * 80)
    
    # Initialize demo
    demo = ChatbotAPIDemo()
    if not await demo.initialize():
        print("❌ Failed to initialize demo")
        return
    
    print("\n" + "=" * 80)
    print("📋 SIMULATING API ENDPOINTS")
    print("=" * 80)
    
    # Test messages covering different intents
    test_messages = [
        "Hi, I need to track my order #12345",
        "What are the ingredients in your organic pasta sauce?",
        "Do you have the blue widgets in stock?",
        "I want to return a defective product",
        "Where is your nearest store location?",
        "This is a completely random message that makes no sense at all"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n{'-' * 60}")
        print(f"🔄 TEST {i}: Processing message")
        print(f"💬 User Input: \"{message}\"")
        
        # Process message
        result = await demo.process_message(message)
        
        # Show API response
        print(demo.format_api_response(result))
        
        # Show internal details
        if "error" not in result:
            print(f"""
🔍 INTERNAL PROCESSING DETAILS:
- Intent Detected: {result['nlu_result'].get('intent', 'unknown')}
- Confidence Score: {result['nlu_result'].get('confidence', 0.0):.2f}
- Entities Found: {result['nlu_result'].get('entities', {})}
- Escalation Needed: {result['response'].get('escalate', False)}
""")
    
    print("\n" + "=" * 80)
    print("🌐 API ENDPOINT SPECIFICATIONS")
    print("=" * 80)
    
    api_docs = """
📡 AVAILABLE API ENDPOINTS:

POST /api/v1/chat
- Description: Process a customer message and return a response
- Request Body: {"message": "string", "user_id": "string"}
- Response: JSON with intent, confidence, entities, response, escalation flag

GET /api/v1/health
- Description: Health check endpoint
- Response: {"status": "healthy", "timestamp": "ISO datetime"}

POST /api/v1/feedback
- Description: Submit feedback on chatbot response
- Request Body: {"conversation_id": "string", "rating": 1-5, "feedback": "string"}

GET /api/v1/intents
- Description: List all available intents and their patterns
- Response: JSON with intent definitions and example patterns

POST /api/v1/context/{user_id}
- Description: Get or update user conversation context
- Response: Current user context and conversation history

GET /api/v1/analytics/summary
- Description: Get analytics summary (requires authentication)
- Headers: {"Authorization": "Bearer <api_key>"}
- Response: Conversation metrics, intent distribution, escalation rates

🔐 AUTHENTICATION:
- API Key required for analytics and admin endpoints
- Header: Authorization: Bearer <your-api-key>
- Rate limiting: 60 requests per minute per IP

📊 RESPONSE FORMATS:
- All responses include status, data, and metadata
- Error responses include error details and troubleshooting hints
- Success responses include confidence scores and processing metadata
"""
    
    print(api_docs)
    
    print("\n" + "=" * 80)
    print("✅ API DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("""
🚀 NEXT STEPS:
1. Start the full API server: uvicorn app:app --host 0.0.0.0 --port 8000
2. Test endpoints with curl or Postman
3. Use the web client: examples/web-client.html
4. Integrate with your application using the Python client: examples/python_client.py

📖 For complete documentation, see: README.md and DEPLOYMENT.md
""")

if __name__ == "__main__":
    try:
        asyncio.run(demonstrate_api_endpoints())
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {str(e)}")
        sys.exit(1)
