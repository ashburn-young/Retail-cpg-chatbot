"""
Retail & CPG Customer Service Chatbot - Main Application
========================================================

A comprehensive AI-powered customer service chatbot template designed specifically
for the retail and consumer packaged goods (CPG) industry.

Features:
- Natural Language Understanding for customer queries
- Dynamic response generation with templates
- Order tracking and inventory management integration
- Conversation context management
- Human escalation when confidence is low
- Comprehensive logging and analytics
- Secure API key management
- Cloud-ready containerized deployment

Author: AI Agent Template
Version: 1.0.0
"""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from config.settings import Settings
from modules.analytics import AnalyticsLogger
from modules.context import ContextManager
from modules.integration import BackendIntegrator

# Import our custom modules
from modules.nlu import NLUProcessor
from modules.response import ResponseGenerator

# Global variables (initialized in lifespan)
settings = None
nlu_processor = None
response_generator = None
context_manager = None
backend_integrator = None
analytics_logger = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("chatbot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()


# Pydantic models for API requests/responses
class ChatMessage(BaseModel):
    """Model for incoming chat messages"""

    message: str = Field(
        ..., min_length=1, max_length=1000, description="Customer message"
    )
    session_id: Optional[str] = Field(
        None, description="Session ID for conversation tracking"
    )
    customer_id: Optional[str] = Field(None, description="Customer ID if authenticated")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ChatResponse(BaseModel):
    """Model for chatbot responses"""

    response: str = Field(..., description="Bot response message")
    session_id: str = Field(..., description="Session ID")
    intent: str = Field(..., description="Detected intent")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Response confidence score"
    )
    escalate_to_human: bool = Field(
        ..., description="Whether to escalate to human agent"
    )
    suggested_actions: Optional[list] = Field(
        default_factory=list, description="Suggested follow-up actions"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="Response timestamp"
    )


class HealthCheck(BaseModel):
    """Health check response model"""

    status: str
    timestamp: datetime
    version: str
    components: Dict[str, str]


# Global components - initialized during startup
settings: Settings
nlu_processor: NLUProcessor
response_generator: ResponseGenerator
context_manager: ContextManager
backend_integrator: BackendIntegrator
analytics_logger: AnalyticsLogger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting Retail & CPG Customer Service Chatbot...")

    global settings, nlu_processor, response_generator, context_manager, backend_integrator, analytics_logger

    try:
        # Initialize settings
        settings = Settings()
        logger.info("✅ Settings loaded successfully")

        # Initialize NLU processor
        nlu_processor = NLUProcessor(settings)
        await nlu_processor.initialize()
        logger.info("✅ NLU processor initialized")

        # Initialize response generator
        response_generator = ResponseGenerator(settings)
        logger.info("✅ Response generator initialized")

        # Initialize context manager
        context_manager = ContextManager(settings)
        await context_manager.initialize()
        logger.info("✅ Context manager initialized")

        # Initialize backend integrator
        backend_integrator = BackendIntegrator(settings)
        await backend_integrator.initialize()
        logger.info("✅ Backend integrator initialized")

        # Initialize analytics logger
        analytics_logger = AnalyticsLogger(settings)
        await analytics_logger.initialize()
        logger.info("✅ Analytics logger initialized")

        logger.info("🎉 Chatbot initialization complete!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Retail & CPG Customer Service Chatbot...")

    # Cleanup resources
    try:
        await context_manager.cleanup()
        await backend_integrator.cleanup()
        await analytics_logger.cleanup()
        logger.info("✅ Cleanup completed successfully")
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="Retail & CPG Customer Service Chatbot",
    description="AI-powered customer service chatbot for retail and CPG industries",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your security requirements
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Security dependency
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API token for secured endpoints"""
    if settings and settings.API_KEY and credentials.credentials != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Retail & CPG Customer Service Chatbot API",
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check component health
        components = {
            "nlu_processor": "healthy" if nlu_processor else "unhealthy",
            "response_generator": "healthy" if response_generator else "unhealthy",
            "context_manager": "healthy" if context_manager else "unhealthy",
            "backend_integrator": "healthy" if backend_integrator else "unhealthy",
            "analytics_logger": "healthy" if analytics_logger else "unhealthy",
        }

        overall_status = (
            "healthy"
            if all(status == "healthy" for status in components.values())
            else "unhealthy"
        )

        return HealthCheck(
            status=overall_status,
            timestamp=datetime.now(),
            version="1.0.0",
            components=components,
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage, request: Request, token: str = Depends(verify_token)
):
    """
    Main chat endpoint for processing customer messages

    This endpoint:
    1. Processes the incoming message using NLU
    2. Manages conversation context
    3. Generates appropriate responses
    4. Integrates with backend systems when needed
    5. Logs interactions for analytics
    6. Determines if human escalation is needed
    """
    try:
        # Check if components are initialized
        if not all(
            [
                nlu_processor,
                response_generator,
                context_manager,
                backend_integrator,
                analytics_logger,
            ]
        ):
            raise HTTPException(status_code=503, detail="Service not fully initialized")

        # Generate session ID if not provided
        session_id = message.session_id or str(uuid.uuid4())

        # Get client IP for logging
        client_ip = request.client.host

        logger.info(
            f"Processing message for session {session_id}: {message.message[:100]}..."
        )

        # Step 1: Natural Language Understanding
        nlu_result = await nlu_processor.process(message.message)
        intent = nlu_result.get("intent", "unknown")
        entities = nlu_result.get("entities", {})
        confidence = nlu_result.get("confidence", 0.0)

        logger.info(f"NLU Result - Intent: {intent}, Confidence: {confidence:.2f}")

        # Step 2: Context Management
        context = await context_manager.get_context(session_id)
        await context_manager.update_context(
            session_id,
            {
                "last_message": message.message,
                "last_intent": intent,
                "last_entities": entities,
                "customer_id": message.customer_id,
                "metadata": message.metadata,
            },
        )

        # Step 3: Backend Integration (if needed)
        backend_data = {}
        if intent in ["track_order", "inventory_check", "product_info"]:
            try:
                backend_data = await backend_integrator.process_request(
                    intent, entities, context, message.customer_id
                )
            except Exception as e:
                logger.warning(f"Backend integration failed: {str(e)}")
                backend_data = {"error": "Backend service temporarily unavailable"}

        # Step 4: Response Generation
        response_data = await response_generator.generate_response(
            intent=intent,
            entities=entities,
            context=context,
            backend_data=backend_data,
            confidence=confidence,
        )

        response_text = response_data.get(
            "response", "I'm sorry, I didn't understand that."
        )
        escalate = response_data.get("escalate_to_human", False)
        suggested_actions = response_data.get("suggested_actions", [])

        # Step 5: Determine escalation need
        if confidence < settings.CONFIDENCE_THRESHOLD:
            escalate = True
            response_text = response_generator.get_escalation_message()

        # Step 6: Analytics Logging
        await analytics_logger.log_interaction(
            session_id=session_id,
            customer_id=message.customer_id,
            message=message.message,
            intent=intent,
            confidence=confidence,
            response=response_text,
            escalated=escalate,
            client_ip=client_ip,
            metadata=message.metadata,
        )

        # Create response
        chat_response = ChatResponse(
            response=response_text,
            session_id=session_id,
            intent=intent,
            confidence=confidence,
            escalate_to_human=escalate,
            suggested_actions=suggested_actions,
            timestamp=datetime.now(),
        )

        logger.info(
            f"Response generated for session {session_id}: {response_text[:100]}..."
        )

        return chat_response

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")

        # Log error for analytics
        try:
            await analytics_logger.log_error(
                session_id=session_id,
                error=str(e),
                message=message.message,
                client_ip=client_ip,
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message. Please try again.",
        )


@app.get("/analytics/summary")
async def get_analytics_summary(token: str = Depends(verify_token), hours: int = 24):
    """Get analytics summary for the specified time period"""
    try:
        if not analytics_logger:
            raise HTTPException(
                status_code=503, detail="Analytics logger not initialized"
            )
        summary = await analytics_logger.get_summary(hours=hours)
        return summary
    except Exception as e:
        logger.error(f"Error retrieving analytics summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")


@app.post("/context/clear/{session_id}")
async def clear_context(session_id: str, token: str = Depends(verify_token)):
    """Clear conversation context for a specific session"""
    try:
        if not context_manager:
            raise HTTPException(
                status_code=503, detail="Context manager not initialized"
            )
        await context_manager.clear_context(session_id)
        return {"message": f"Context cleared for session {session_id}"}
    except Exception as e:
        logger.error(f"Error clearing context: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear context")


@app.get("/intents")
async def get_supported_intents(token: str = Depends(verify_token)):
    """Get list of supported intents"""
    try:
        if not nlu_processor:
            raise HTTPException(status_code=503, detail="NLU processor not initialized")
        intents = nlu_processor.get_supported_intents()
        return {"intents": intents}
    except Exception as e:
        logger.error(f"Error retrieving intents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve intents")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found", "path": str(request.url.path)},
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": "Please try again later",
        },
    )


if __name__ == "__main__":
    import uvicorn

    # Load settings for development
    dev_settings = Settings()

    uvicorn.run(
        "app:app", host="0.0.0.0", port=dev_settings.PORT, reload=True, log_level="info"
    )
