"""
Analytics Module
===============

This module handles logging and analytics for the retail & CPG chatbot.
It tracks user interactions, conversation patterns, and system performance
to provide insights for improving the chatbot experience.

Features:
- Interaction logging with structured data
- Performance metrics tracking
- User behavior analytics
- Error tracking and alerting
- Real-time dashboard data
- Privacy-compliant data handling
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from pathlib import Path

from config.settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class InteractionLog:
    """Structure for logging user interactions"""
    timestamp: datetime
    session_id: str
    customer_id: Optional[str]
    message: str
    intent: str
    confidence: float
    response: str
    escalated: bool
    response_time: Optional[float] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionLog':
        """Create from dictionary"""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


@dataclass
class ErrorLog:
    """Structure for logging errors"""
    timestamp: datetime
    session_id: str
    error_type: str
    error_message: str
    user_message: Optional[str] = None
    stack_trace: Optional[str] = None
    client_ip: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class PerformanceMetric:
    """Structure for performance metrics"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class AnalyticsStorage:
    """Base class for analytics storage"""
    
    async def log_interaction(self, interaction: InteractionLog):
        """Log user interaction"""
        raise NotImplementedError
    
    async def log_error(self, error: ErrorLog):
        """Log error"""
        raise NotImplementedError
    
    async def log_metric(self, metric: PerformanceMetric):
        """Log performance metric"""
        raise NotImplementedError
    
    async def get_interactions(self, start_time: datetime, end_time: datetime) -> List[InteractionLog]:
        """Get interactions in time range"""
        raise NotImplementedError


class FileAnalyticsStorage(AnalyticsStorage):
    """File-based analytics storage"""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
        self.interactions_file = self.base_path / "interactions.jsonl"
        self.errors_file = self.base_path / "errors.jsonl"
        self.metrics_file = self.base_path / "metrics.jsonl"
        
        # Create files if they don't exist
        for file_path in [self.interactions_file, self.errors_file, self.metrics_file]:
            if not file_path.exists():
                file_path.touch()
    
    async def log_interaction(self, interaction: InteractionLog):
        """Log user interaction to file"""
        try:
            with open(self.interactions_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(interaction.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Failed to log interaction: {str(e)}")
    
    async def log_error(self, error: ErrorLog):
        """Log error to file"""
        try:
            with open(self.errors_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(error.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
    
    async def log_metric(self, metric: PerformanceMetric):
        """Log performance metric to file"""
        try:
            with open(self.metrics_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(metric.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Failed to log metric: {str(e)}")
    
    async def get_interactions(self, start_time: datetime, end_time: datetime) -> List[InteractionLog]:
        """Get interactions in time range from file"""
        interactions = []
        
        try:
            with open(self.interactions_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        timestamp = datetime.fromisoformat(data["timestamp"])
                        
                        if start_time <= timestamp <= end_time:
                            interactions.append(InteractionLog.from_dict(data))
        except Exception as e:
            logger.error(f"Failed to read interactions: {str(e)}")
        
        return interactions


class AnalyticsLogger:
    """
    Main analytics and logging coordinator
    
    This class provides:
    - Structured interaction logging
    - Performance metrics collection
    - Error tracking and reporting
    - Analytics data aggregation
    - Real-time insights generation
    """
    
    def __init__(self, settings: Settings):
        """Initialize analytics logger with settings"""
        self.settings = settings
        self.storage: Optional[AnalyticsStorage] = None
        self.metrics_cache = defaultdict(list)
        self.cache_lock = asyncio.Lock()
        
        # Analytics configuration
        self.enabled = settings.ANALYTICS_ENABLED
        
        # Performance tracking
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        
    async def initialize(self):
        """Initialize the analytics logger"""
        try:
            logger.info("Initializing analytics logger...")
            
            if not self.enabled:
                logger.info("Analytics disabled in settings")
                return
            
            # Initialize storage backend
            storage_type = self.settings.ANALYTICS_STORAGE_TYPE.lower()
            
            if storage_type == "file":
                analytics_path = Path(self.settings.ANALYTICS_FILE_PATH).parent
                self.storage = FileAnalyticsStorage(str(analytics_path))
            else:
                # Default to file storage
                self.storage = FileAnalyticsStorage()
                logger.warning(f"Unknown storage type {storage_type}, using file storage")
            
            logger.info("✅ Analytics logger initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics logger: {str(e)}")
            raise
    
    async def log_interaction(
        self,
        session_id: str,
        customer_id: Optional[str],
        message: str,
        intent: str,
        confidence: float,
        response: str,
        escalated: bool = False,
        response_time: Optional[float] = None,
        client_ip: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log a user interaction"""
        
        if not self.enabled or not self.storage:
            return
        
        try:
            interaction = InteractionLog(
                timestamp=datetime.now(),
                session_id=session_id,
                customer_id=customer_id,
                message=message[:500],  # Truncate long messages for privacy
                intent=intent,
                confidence=confidence,
                response=response[:500],  # Truncate long responses
                escalated=escalated,
                response_time=response_time,
                client_ip=client_ip,
                metadata=metadata or {}
            )
            
            await self.storage.log_interaction(interaction)
            
            # Update counters
            self.request_count += 1
            
            # Log performance metrics
            await self._log_performance_metrics(interaction)
            
        except Exception as e:
            logger.error(f"Failed to log interaction: {str(e)}")
    
    async def log_error(
        self,
        session_id: str,
        error: str,
        message: Optional[str] = None,
        client_ip: Optional[str] = None,
        stack_trace: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log an error"""
        
        if not self.enabled or not self.storage:
            return
        
        try:
            error_log = ErrorLog(
                timestamp=datetime.now(),
                session_id=session_id,
                error_type="chatbot_error",
                error_message=error,
                user_message=message,
                stack_trace=stack_trace,
                client_ip=client_ip,
                metadata=metadata or {}
            )
            
            await self.storage.log_error(error_log)
            
            # Update error counter
            self.error_count += 1
            
        except Exception as e:
            logger.error(f"Failed to log error: {str(e)}")
    
    async def _log_performance_metrics(self, interaction: InteractionLog):
        """Log performance metrics based on interaction"""
        
        timestamp = datetime.now()
        
        # Response time metric
        if interaction.response_time:
            metric = PerformanceMetric(
                timestamp=timestamp,
                metric_name="response_time",
                value=interaction.response_time,
                unit="seconds",
                tags={"intent": interaction.intent}
            )
            await self.storage.log_metric(metric)
        
        # Confidence metric
        confidence_metric = PerformanceMetric(
            timestamp=timestamp,
            metric_name="confidence",
            value=interaction.confidence,
            unit="score",
            tags={"intent": interaction.intent}
        )
        await self.storage.log_metric(confidence_metric)
        
        # Escalation metric
        escalation_metric = PerformanceMetric(
            timestamp=timestamp,
            metric_name="escalation",
            value=1.0 if interaction.escalated else 0.0,
            unit="boolean",
            tags={"intent": interaction.intent}
        )
        await self.storage.log_metric(escalation_metric)
    
    async def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get analytics summary for the specified time period"""
        
        if not self.enabled or not self.storage:
            return {"message": "Analytics not enabled"}
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Get interactions in time range
            interactions = await self.storage.get_interactions(start_time, end_time)
            
            if not interactions:
                return {
                    "period": f"Last {hours} hours",
                    "total_interactions": 0,
                    "message": "No interactions in this period"
                }
            
            # Calculate metrics
            summary = await self._calculate_summary_metrics(interactions, hours)
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {str(e)}")
            return {"error": str(e)}
    
    async def _calculate_summary_metrics(self, interactions: List[InteractionLog], hours: int) -> Dict[str, Any]:
        """Calculate summary metrics from interactions"""
        
        total_interactions = len(interactions)
        
        # Intent distribution
        intent_counts = Counter(interaction.intent for interaction in interactions)
        
        # Confidence statistics
        confidences = [interaction.confidence for interaction in interactions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Escalation rate
        escalations = sum(1 for interaction in interactions if interaction.escalated)
        escalation_rate = escalations / total_interactions if total_interactions > 0 else 0
        
        # Response time statistics
        response_times = [interaction.response_time for interaction in interactions if interaction.response_time]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Session statistics
        unique_sessions = len(set(interaction.session_id for interaction in interactions))
        
        # Customer statistics
        unique_customers = len(set(
            interaction.customer_id for interaction in interactions 
            if interaction.customer_id
        ))
        
        # Popular intents (top 5)
        top_intents = intent_counts.most_common(5)
        
        # Time distribution (interactions per hour)
        hourly_distribution = defaultdict(int)
        for interaction in interactions:
            hour = interaction.timestamp.hour
            hourly_distribution[hour] += 1
        
        return {
            "period": f"Last {hours} hours",
            "total_interactions": total_interactions,
            "unique_sessions": unique_sessions,
            "unique_customers": unique_customers,
            "average_confidence": round(avg_confidence, 3),
            "escalation_rate": round(escalation_rate, 3),
            "average_response_time": round(avg_response_time, 3) if avg_response_time else None,
            "top_intents": [{"intent": intent, "count": count} for intent, count in top_intents],
            "hourly_distribution": dict(hourly_distribution),
            "performance": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": round(self.error_count / max(self.request_count, 1), 3),
                "uptime_hours": round((datetime.now() - self.start_time).total_seconds() / 3600, 2)
            }
        }
    
    async def get_intent_analytics(self, intent: str, hours: int = 24) -> Dict[str, Any]:
        """Get analytics for a specific intent"""
        
        if not self.enabled or not self.storage:
            return {"message": "Analytics not enabled"}
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            interactions = await self.storage.get_interactions(start_time, end_time)
            intent_interactions = [i for i in interactions if i.intent == intent]
            
            if not intent_interactions:
                return {
                    "intent": intent,
                    "period": f"Last {hours} hours",
                    "total_interactions": 0,
                    "message": "No interactions for this intent"
                }
            
            # Calculate intent-specific metrics
            total_count = len(intent_interactions)
            confidences = [i.confidence for i in intent_interactions]
            avg_confidence = sum(confidences) / len(confidences)
            
            escalations = sum(1 for i in intent_interactions if i.escalated)
            escalation_rate = escalations / total_count
            
            # Low confidence interactions (for improvement)
            low_confidence_threshold = 0.7
            low_confidence_count = sum(1 for c in confidences if c < low_confidence_threshold)
            
            return {
                "intent": intent,
                "period": f"Last {hours} hours",
                "total_interactions": total_count,
                "average_confidence": round(avg_confidence, 3),
                "escalation_rate": round(escalation_rate, 3),
                "low_confidence_interactions": low_confidence_count,
                "improvement_potential": round(low_confidence_count / total_count, 3) if total_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get intent analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        
        uptime = datetime.now() - self.start_time
        
        return {
            "status": "healthy",
            "uptime_seconds": uptime.total_seconds(),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": round(self.error_count / max(self.request_count, 1), 3),
            "requests_per_minute": round(self.request_count / max(uptime.total_seconds() / 60, 1), 2),
            "last_updated": datetime.now().isoformat()
        }
    
    async def export_data(self, start_time: datetime, end_time: datetime, format: str = "json") -> str:
        """Export analytics data for the specified time range"""
        
        if not self.enabled or not self.storage:
            return "Analytics not enabled"
        
        try:
            interactions = await self.storage.get_interactions(start_time, end_time)
            
            if format.lower() == "json":
                export_data = {
                    "export_info": {
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "total_interactions": len(interactions),
                        "exported_at": datetime.now().isoformat()
                    },
                    "interactions": [interaction.to_dict() for interaction in interactions]
                }
                
                return json.dumps(export_data, indent=2)
            
            else:
                return "Unsupported export format"
                
        except Exception as e:
            logger.error(f"Failed to export data: {str(e)}")
            return f"Export failed: {str(e)}"
    
    async def cleanup(self):
        """Cleanup resources"""
        # Perform any necessary cleanup
        pass


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from config.settings import Settings
    
    async def test_analytics_logger():
        """Test the analytics logger"""
        settings = Settings()
        analytics = AnalyticsLogger(settings)
        await analytics.initialize()
        
        print("Testing Analytics Logger")
        print("=" * 50)
        
        # Test logging interactions
        await analytics.log_interaction(
            session_id="test_session_1",
            customer_id="customer_123",
            message="I want to track my order",
            intent="track_order",
            confidence=0.95,
            response="I'll help you track your order",
            response_time=0.5
        )
        
        await analytics.log_interaction(
            session_id="test_session_2",
            customer_id="customer_456",
            message="What's the price of iPhone?",
            intent="pricing",
            confidence=0.88,
            response="Let me get pricing information",
            response_time=0.7
        )
        
        # Test error logging
        await analytics.log_error(
            session_id="test_session_1",
            error="Backend service unavailable",
            message="Check my order status"
        )
        
        # Get summary
        summary = await analytics.get_summary(hours=1)
        print(f"Analytics summary: {json.dumps(summary, indent=2)}")
        
        # Get real-time metrics
        metrics = await analytics.get_real_time_metrics()
        print(f"Real-time metrics: {json.dumps(metrics, indent=2)}")
        
        # Get intent analytics
        intent_analytics = await analytics.get_intent_analytics("track_order", hours=1)
        print(f"Intent analytics: {json.dumps(intent_analytics, indent=2)}")
        
        await analytics.cleanup()
    
    # Run test
    asyncio.run(test_analytics_logger())
