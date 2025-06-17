"""
Context Management Module
========================

This module handles conversation context and state management for the retail & CPG chatbot.
It maintains conversation history, user preferences, and session data to enable
more natural and contextual interactions.

Features:
- Session-based context storage
- Conversation history tracking
- User preference management
- Context expiration and cleanup
- Multi-storage backend support (memory, Redis, database)
- Context analytics and insights
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation"""

    timestamp: datetime
    user_message: str
    bot_response: str
    intent: str
    entities: Dict[str, Any]
    confidence: float
    escalated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "user_message": self.user_message,
            "bot_response": self.bot_response,
            "intent": self.intent,
            "entities": self.entities,
            "confidence": self.confidence,
            "escalated": self.escalated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationTurn":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_message=data["user_message"],
            bot_response=data["bot_response"],
            intent=data["intent"],
            entities=data["entities"],
            confidence=data["confidence"],
            escalated=data.get("escalated", False),
        )


@dataclass
class CustomerProfile:
    """Customer profile and preferences"""

    customer_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: str = "en"
    customer_type: str = "unknown"  # new, returning, vip, etc.
    last_order_date: Optional[datetime] = None
    total_orders: int = 0
    preferred_contact_method: str = "chat"
    interests: List[str] = None
    location: Optional[str] = None

    def __post_init__(self):
        if self.interests is None:
            self.interests = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        if self.last_order_date:
            data["last_order_date"] = self.last_order_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CustomerProfile":
        """Create from dictionary"""
        if data.get("last_order_date"):
            data["last_order_date"] = datetime.fromisoformat(data["last_order_date"])
        return cls(**data)


@dataclass
class SessionContext:
    """Complete session context"""

    session_id: str
    created_at: datetime
    last_updated: datetime
    customer_profile: CustomerProfile
    conversation_history: List[ConversationTurn]
    current_intent: Optional[str] = None
    current_entities: Dict[str, Any] = None
    context_variables: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    turn_count: int = 0

    def __post_init__(self):
        if self.current_entities is None:
            self.current_entities = {}
        if self.context_variables is None:
            self.context_variables = {}
        if self.metadata is None:
            self.metadata = {}

    def add_turn(self, turn: ConversationTurn):
        """Add a new conversation turn"""
        self.conversation_history.append(turn)
        self.turn_count += 1
        self.last_updated = datetime.now()
        self.current_intent = turn.intent
        self.current_entities = turn.entities

    def get_recent_turns(self, count: int = 3) -> List[ConversationTurn]:
        """Get the most recent conversation turns"""
        return self.conversation_history[-count:] if self.conversation_history else []

    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation"""
        if not self.conversation_history:
            return "No conversation history"

        intents = [turn.intent for turn in self.conversation_history]
        intent_summary = ", ".join(set(intents))

        return (
            f"Session with {self.turn_count} turns. Intents discussed: {intent_summary}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "customer_profile": self.customer_profile.to_dict(),
            "conversation_history": [
                turn.to_dict() for turn in self.conversation_history
            ],
            "current_intent": self.current_intent,
            "current_entities": self.current_entities,
            "context_variables": self.context_variables,
            "metadata": self.metadata,
            "turn_count": self.turn_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionContext":
        """Create from dictionary"""
        return cls(
            session_id=data["session_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            customer_profile=CustomerProfile.from_dict(data["customer_profile"]),
            conversation_history=[
                ConversationTurn.from_dict(turn_data)
                for turn_data in data["conversation_history"]
            ],
            current_intent=data.get("current_intent"),
            current_entities=data.get("current_entities", {}),
            context_variables=data.get("context_variables", {}),
            metadata=data.get("metadata", {}),
            turn_count=data.get("turn_count", 0),
        )


class ContextStorage(ABC):
    """Abstract base class for context storage backends"""

    @abstractmethod
    async def get(self, session_id: str) -> Optional[SessionContext]:
        """Get session context by ID"""
        pass

    @abstractmethod
    async def set(self, session_id: str, context: SessionContext) -> bool:
        """Store session context"""
        pass

    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """Delete session context"""
        pass

    @abstractmethod
    async def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        pass

    @abstractmethod
    async def cleanup_expired(self, ttl_minutes: int) -> int:
        """Clean up expired sessions"""
        pass


class MemoryContextStorage(ContextStorage):
    """In-memory context storage (for development and testing)"""

    def __init__(self):
        self.contexts: Dict[str, SessionContext] = {}
        self.lock = asyncio.Lock()

    async def get(self, session_id: str) -> Optional[SessionContext]:
        """Get session context by ID"""
        async with self.lock:
            return self.contexts.get(session_id)

    async def set(self, session_id: str, context: SessionContext) -> bool:
        """Store session context"""
        async with self.lock:
            self.contexts[session_id] = context
            return True

    async def delete(self, session_id: str) -> bool:
        """Delete session context"""
        async with self.lock:
            if session_id in self.contexts:
                del self.contexts[session_id]
                return True
            return False

    async def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        async with self.lock:
            return session_id in self.contexts

    async def cleanup_expired(self, ttl_minutes: int) -> int:
        """Clean up expired sessions"""
        cutoff_time = datetime.now() - timedelta(minutes=ttl_minutes)
        expired_sessions = []

        async with self.lock:
            for session_id, context in self.contexts.items():
                if context.last_updated < cutoff_time:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                del self.contexts[session_id]

        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)

    async def get_all_sessions(self) -> List[str]:
        """Get all session IDs (for testing)"""
        async with self.lock:
            return list(self.contexts.keys())


class RedisContextStorage(ContextStorage):
    """Redis-based context storage (for production)"""

    def __init__(self, redis_url: str, password: Optional[str] = None):
        self.redis_url = redis_url
        self.password = password
        self.redis = None

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as redis

            self.redis = redis.from_url(
                self.redis_url, password=self.password, decode_responses=True
            )
            await self.redis.ping()
            logger.info("✅ Redis context storage initialized")
        except ImportError:
            raise RuntimeError(
                "Redis package not installed. Install with: pip install redis"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
            raise

    async def get(self, session_id: str) -> Optional[SessionContext]:
        """Get session context by ID"""
        try:
            data = await self.redis.get(f"context:{session_id}")
            if data:
                context_dict = json.loads(data)
                return SessionContext.from_dict(context_dict)
            return None
        except Exception as e:
            logger.error(f"Error getting context from Redis: {str(e)}")
            return None

    async def set(self, session_id: str, context: SessionContext) -> bool:
        """Store session context"""
        try:
            data = json.dumps(context.to_dict())
            await self.redis.set(
                f"context:{session_id}", data, ex=3600
            )  # 1 hour expiration
            return True
        except Exception as e:
            logger.error(f"Error storing context in Redis: {str(e)}")
            return False

    async def delete(self, session_id: str) -> bool:
        """Delete session context"""
        try:
            result = await self.redis.delete(f"context:{session_id}")
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting context from Redis: {str(e)}")
            return False

    async def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        try:
            return await self.redis.exists(f"context:{session_id}") > 0
        except Exception as e:
            logger.error(f"Error checking context existence in Redis: {str(e)}")
            return False

    async def cleanup_expired(self, ttl_minutes: int) -> int:
        """Redis handles expiration automatically"""
        return 0


class ContextManager:
    """
    Manages conversation context and session state

    This class provides:
    - Session creation and management
    - Context storage and retrieval
    - Conversation history tracking
    - Customer profile management
    - Context analytics
    """

    def __init__(self, settings: Settings):
        """Initialize context manager with settings"""
        self.settings = settings
        self.storage: Optional[ContextStorage] = None
        self.cleanup_task = None

    async def initialize(self):
        """Initialize the context manager"""
        try:
            logger.info("Initializing context manager...")

            # Initialize storage backend
            storage_type = self.settings.CONTEXT_STORAGE_TYPE.lower()

            if storage_type == "redis" and self.settings.REDIS_URL:
                self.storage = RedisContextStorage(
                    self.settings.REDIS_URL, self.settings.REDIS_PASSWORD
                )
                await self.storage.initialize()
            else:
                self.storage = MemoryContextStorage()
                logger.info("Using in-memory context storage")

            # Start cleanup task
            self._start_cleanup_task()

            logger.info("✅ Context manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize context manager: {str(e)}")
            raise

    async def get_context(self, session_id: str) -> Dict[str, Any]:
        """
        Get or create session context

        Returns a simplified context dictionary for use in response generation
        """
        try:
            # Get existing context
            context = await self.storage.get(session_id)

            if not context:
                # Create new context
                context = SessionContext(
                    session_id=session_id,
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    customer_profile=CustomerProfile(),
                    conversation_history=[],
                )
                await self.storage.set(session_id, context)

            # Return simplified context for response generation
            return {
                "session_id": session_id,
                "customer_id": context.customer_profile.customer_id,
                "customer_type": context.customer_profile.customer_type,
                "turn_count": context.turn_count,
                "last_intent": context.current_intent,
                "last_entities": context.current_entities,
                "conversation_history": " ".join(
                    [turn.user_message for turn in context.get_recent_turns(3)]
                ),
                "context_variables": context.context_variables,
                "metadata": context.metadata,
            }

        except Exception as e:
            logger.error(f"Error getting context: {str(e)}")
            return {"session_id": session_id, "error": str(e)}

    async def update_context(
        self,
        session_id: str,
        updates: Dict[str, Any],
        user_message: Optional[str] = None,
        bot_response: Optional[str] = None,
    ):
        """Update session context with new information"""
        try:
            # Get existing context
            context = await self.storage.get(session_id)

            if not context:
                # Create new context if it doesn't exist
                context = SessionContext(
                    session_id=session_id,
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    customer_profile=CustomerProfile(),
                    conversation_history=[],
                )

            # Update customer profile
            if "customer_id" in updates:
                context.customer_profile.customer_id = updates["customer_id"]

            # Update context variables
            if "metadata" in updates:
                context.metadata.update(updates["metadata"])

            # Add conversation turn if provided
            if user_message and bot_response:
                turn = ConversationTurn(
                    timestamp=datetime.now(),
                    user_message=user_message,
                    bot_response=bot_response,
                    intent=updates.get("last_intent", "unknown"),
                    entities=updates.get("last_entities", {}),
                    confidence=updates.get("confidence", 0.0),
                    escalated=updates.get("escalated", False),
                )
                context.add_turn(turn)

            # Update other fields
            for key, value in updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)
                else:
                    context.context_variables[key] = value

            # Trim conversation history if it gets too long
            max_history = self.settings.MAX_CONTEXT_HISTORY
            if len(context.conversation_history) > max_history:
                context.conversation_history = context.conversation_history[
                    -max_history:
                ]

            # Update timestamp
            context.last_updated = datetime.now()

            # Save updated context
            await self.storage.set(session_id, context)

        except Exception as e:
            logger.error(f"Error updating context: {str(e)}")

    async def clear_context(self, session_id: str) -> bool:
        """Clear session context"""
        try:
            return await self.storage.delete(session_id)
        except Exception as e:
            logger.error(f"Error clearing context: {str(e)}")
            return False

    async def get_full_context(self, session_id: str) -> Optional[SessionContext]:
        """Get full session context (for debugging/analytics)"""
        try:
            return await self.storage.get(session_id)
        except Exception as e:
            logger.error(f"Error getting full context: {str(e)}")
            return None

    async def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        try:
            context = await self.storage.get(session_id)
            if context:
                return [turn.to_dict() for turn in context.conversation_history]
            return []
        except Exception as e:
            logger.error(f"Error getting conversation history: {str(e)}")
            return []

    async def update_customer_profile(
        self, session_id: str, profile_updates: Dict[str, Any]
    ):
        """Update customer profile information"""
        try:
            context = await self.storage.get(session_id)
            if context:
                for key, value in profile_updates.items():
                    if hasattr(context.customer_profile, key):
                        setattr(context.customer_profile, key, value)

                context.last_updated = datetime.now()
                await self.storage.set(session_id, context)

        except Exception as e:
            logger.error(f"Error updating customer profile: {str(e)}")

    async def get_analytics_data(self) -> Dict[str, Any]:
        """Get context analytics data"""
        try:
            # This would be implemented differently for different storage types
            if isinstance(self.storage, MemoryContextStorage):
                sessions = await self.storage.get_all_sessions()

                total_sessions = len(sessions)
                active_sessions = 0
                total_turns = 0

                cutoff_time = datetime.now() - timedelta(hours=1)

                for session_id in sessions:
                    context = await self.storage.get(session_id)
                    if context:
                        if context.last_updated > cutoff_time:
                            active_sessions += 1
                        total_turns += context.turn_count

                return {
                    "total_sessions": total_sessions,
                    "active_sessions_last_hour": active_sessions,
                    "average_turns_per_session": total_turns / max(total_sessions, 1),
                    "total_conversation_turns": total_turns,
                }

            return {"message": "Analytics not available for this storage type"}

        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return {"error": str(e)}

    def _start_cleanup_task(self):
        """Start background task for cleaning up expired contexts"""

        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    await self.storage.cleanup_expired(
                        self.settings.CONTEXT_TTL_MINUTES
                    )
                except Exception as e:
                    logger.error(f"Error in cleanup task: {str(e)}")

        self.cleanup_task = asyncio.create_task(cleanup_loop())

    async def cleanup(self):
        """Cleanup resources"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from config.settings import Settings

    async def test_context_manager():
        """Test the context manager"""
        settings = Settings()
        manager = ContextManager(settings)
        await manager.initialize()

        session_id = "test_session_123"

        print("Testing Context Manager")
        print("=" * 50)

        # Test getting new context
        context = await manager.get_context(session_id)
        print(f"New context: {context}")

        # Test updating context
        await manager.update_context(
            session_id,
            {
                "customer_id": "customer_456",
                "last_intent": "track_order",
                "last_entities": {"order_number": ["AB123"]},
                "metadata": {"source": "web"},
            },
            user_message="I want to track my order AB123",
            bot_response="I'll help you track your order.",
        )

        # Test getting updated context
        updated_context = await manager.get_context(session_id)
        print(f"Updated context: {updated_context}")

        # Test conversation history
        history = await manager.get_conversation_history(session_id)
        print(f"Conversation history: {history}")

        # Test analytics
        analytics = await manager.get_analytics_data()
        print(f"Analytics: {analytics}")

        # Cleanup
        await manager.cleanup()

    # Run test
    asyncio.run(test_context_manager())
