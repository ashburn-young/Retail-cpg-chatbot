"""
Configuration Settings for Retail & CPG Customer Service Chatbot
================================================================

This module contains all configuration settings for the chatbot application.
Settings can be overridden using environment variables for different deployment environments.

Security Best Practices:
- All sensitive data (API keys, secrets) should be provided via environment variables
- Never commit secrets to version control
- Use different configuration profiles for development, staging, and production
"""

import os
from typing import Dict, List, Optional
from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support
    
    Environment variables will override default values.
    Example: Set CHATBOT_API_KEY environment variable to override API_KEY
    """
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    
    APP_NAME: str = Field(
        default="Retail & CPG Customer Service Chatbot",
        description="Application name"
    )
    
    VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    
    ENVIRONMENT: str = Field(
        default="development",
        description="Environment: development, staging, production"
    )
    
    DEBUG: bool = Field(
        default=True,
        description="Enable debug mode"
    )
    
    PORT: int = Field(
        default=8000,
        description="Server port"
    )
    
    HOST: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    
    API_KEY: Optional[str] = Field(
        default=None,
        description="API key for authentication (set via CHATBOT_API_KEY env var)"
    )
    
    JWT_SECRET_KEY: Optional[str] = Field(
        default=None,
        description="JWT secret key for token signing"
    )
    
    ALLOWED_ORIGINS: List[str] = Field(
        default=["*"],
        description="CORS allowed origins"
    )
    
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit per minute per IP"
    )
    
    # =============================================================================
    # NLU (NATURAL LANGUAGE UNDERSTANDING) SETTINGS
    # =============================================================================
    
    NLU_MODEL_PATH: str = Field(
        default="en_core_web_sm",
        description="spaCy model for NLU processing"
    )
    
    CONFIDENCE_THRESHOLD: float = Field(
        default=0.7,
        description="Minimum confidence threshold for automated responses"
    )
    
    MAX_MESSAGE_LENGTH: int = Field(
        default=1000,
        description="Maximum length of customer messages"
    )
    
    # Custom intent patterns for retail/CPG domain
    INTENT_PATTERNS: Dict[str, List[str]] = Field(
        default={
            "track_order": [
                "track my order", "order status", "where is my order", "order tracking",
                "check order", "order number", "shipment status", "delivery status"
            ],
            "product_info": [
                "product information", "tell me about", "product details", "specifications",
                "ingredients", "nutritional facts", "product availability", "in stock"
            ],
            "inventory_check": [
                "in stock", "available", "inventory", "stock level", "out of stock",
                "when available", "restock", "availability"
            ],
            "store_locator": [
                "store location", "find store", "nearest store", "store hours",
                "store address", "contact store"
            ],
            "pricing": [
                "price", "cost", "how much", "pricing", "discount", "sale", "promotion"
            ],
            "complaint": [
                "complaint", "problem", "issue", "defective", "broken", "damaged",
                "refund", "return", "exchange"
            ],
            "shipping_info": [
                "shipping", "delivery", "shipping cost", "delivery time", "shipping options"
            ],
            "account_help": [
                "account", "login", "password", "profile", "personal information"
            ],
            "general_inquiry": [
                "help", "support", "question", "information", "contact"
            ]
        }
    )
    
    # =============================================================================
    # RESPONSE GENERATION SETTINGS
    # =============================================================================
    
    RESPONSE_TEMPLATES: Dict[str, str] = Field(
        default={
            "greeting": "Hello! I'm here to help you with your retail and product questions. How can I assist you today?",
            "track_order": "I'd be happy to help you track your order. Your order {order_number} is currently {status}. {additional_info}",
            "product_info": "Here's the information about {product_name}: {product_details}",
            "inventory_check": "Let me check the availability of {product_name}. {stock_status}",
            "store_locator": "I found {store_count} stores near you. The closest one is {store_name} at {store_address}.",
            "pricing": "The current price for {product_name} is {price}. {promotion_info}",
            "escalation": "I'd like to connect you with one of our customer service representatives who can better assist you. Please hold while I transfer you.",
            "error": "I apologize, but I'm having trouble processing your request right now. Please try again or speak with a human agent.",
            "fallback": "I'm not sure I understand. Could you please rephrase your question or ask about orders, products, or store information?"
        }
    )
    
    ESCALATION_KEYWORDS: List[str] = Field(
        default=[
            "angry", "frustrated", "supervisor", "manager", "human", "person",
            "terrible", "awful", "horrible", "lawsuit", "legal"
        ]
    )
    
    # =============================================================================
    # BACKEND INTEGRATION SETTINGS
    # =============================================================================
    
    # Order Management System
    ORDER_API_BASE_URL: str = Field(
        default="https://api.example.com/orders",
        description="Base URL for order management API"
    )
    
    ORDER_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for order management system"
    )
    
    # Inventory Management System
    INVENTORY_API_BASE_URL: str = Field(
        default="https://api.example.com/inventory",
        description="Base URL for inventory management API"
    )
    
    INVENTORY_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for inventory management system"
    )
    
    # Product Information System
    PRODUCT_API_BASE_URL: str = Field(
        default="https://api.example.com/products",
        description="Base URL for product information API"
    )
    
    PRODUCT_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for product information system"
    )
    
    # Store Locator System
    STORE_API_BASE_URL: str = Field(
        default="https://api.example.com/stores",
        description="Base URL for store locator API"
    )
    
    STORE_API_KEY: Optional[str] = Field(
        default=None,
        description="API key for store locator system"
    )
    
    # API timeout settings
    API_TIMEOUT_SECONDS: int = Field(
        default=10,
        description="Timeout for backend API calls"
    )
    
    API_RETRY_COUNT: int = Field(
        default=3,
        description="Number of retries for failed API calls"
    )
    
    # =============================================================================
    # CONTEXT MANAGEMENT SETTINGS
    # =============================================================================
    
    CONTEXT_STORAGE_TYPE: str = Field(
        default="memory",
        description="Context storage type: memory, redis, database"
    )
    
    CONTEXT_TTL_MINUTES: int = Field(
        default=30,
        description="Context time-to-live in minutes"
    )
    
    MAX_CONTEXT_HISTORY: int = Field(
        default=10,
        description="Maximum number of conversation turns to keep in context"
    )
    
    # Redis settings (if using Redis for context storage)
    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection URL"
    )
    
    REDIS_PASSWORD: Optional[str] = Field(
        default=None,
        description="Redis password"
    )
    
    # =============================================================================
    # ANALYTICS AND LOGGING SETTINGS
    # =============================================================================
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    
    LOG_FILE_PATH: str = Field(
        default="logs/chatbot.log",
        description="Path to log file"
    )
    
    ANALYTICS_ENABLED: bool = Field(
        default=True,
        description="Enable analytics logging"
    )
    
    ANALYTICS_STORAGE_TYPE: str = Field(
        default="file",
        description="Analytics storage: file, database, cloud"
    )
    
    ANALYTICS_FILE_PATH: str = Field(
        default="data/analytics.jsonl",
        description="Path to analytics file"
    )
    
    # Database settings (if using database for analytics)
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Database connection URL"
    )
    
    # =============================================================================
    # BRANDING AND CUSTOMIZATION
    # =============================================================================
    
    COMPANY_NAME: str = Field(
        default="Your Retail Company",
        description="Company name for branding"
    )
    
    COMPANY_WEBSITE: str = Field(
        default="https://www.yourcompany.com",
        description="Company website URL"
    )
    
    SUPPORT_EMAIL: str = Field(
        default="support@yourcompany.com",
        description="Support email address"
    )
    
    SUPPORT_PHONE: str = Field(
        default="1-800-YOUR-HELP",
        description="Support phone number"
    )
    
    BRAND_COLOR: str = Field(
        default="#007bff",
        description="Primary brand color (hex code)"
    )
    
    LOGO_URL: Optional[str] = Field(
        default=None,
        description="URL to company logo"
    )
    
    # =============================================================================
    # BUSINESS RULES
    # =============================================================================
    
    BUSINESS_HOURS: Dict[str, str] = Field(
        default={
            "monday": "9:00-17:00",
            "tuesday": "9:00-17:00",
            "wednesday": "9:00-17:00",
            "thursday": "9:00-17:00",
            "friday": "9:00-17:00",
            "saturday": "10:00-16:00",
            "sunday": "closed"
        }
    )
    
    TIMEZONE: str = Field(
        default="UTC",
        description="Business timezone"
    )
    
    # Order status mappings
    ORDER_STATUS_MAPPING: Dict[str, str] = Field(
        default={
            "pending": "Your order has been received and is being processed.",
            "processing": "Your order is currently being prepared for shipment.",
            "shipped": "Your order has been shipped and is on its way to you.",
            "delivered": "Your order has been successfully delivered.",
            "cancelled": "Your order has been cancelled.",
            "returned": "Your order has been returned and is being processed for refund."
        }
    )
    
    # =============================================================================
    # VALIDATORS
    # =============================================================================
    
    @validator('ENVIRONMENT')
    def validate_environment(cls, v):
        """Validate environment setting"""
        allowed_environments = ['development', 'staging', 'production']
        if v not in allowed_environments:
            raise ValueError(f'Environment must be one of: {allowed_environments}')
        return v
    
    @validator('CONFIDENCE_THRESHOLD')
    def validate_confidence_threshold(cls, v):
        """Validate confidence threshold is between 0 and 1"""
        if not 0 <= v <= 1:
            raise ValueError('Confidence threshold must be between 0 and 1')
        return v
    
    @validator('LOG_LEVEL')
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in allowed_levels:
            raise ValueError(f'Log level must be one of: {allowed_levels}')
        return v.upper()
    
    class Config:
        """Pydantic configuration"""
        env_prefix = "CHATBOT_"
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# =============================================================================
# ENVIRONMENT-SPECIFIC CONFIGURATIONS
# =============================================================================

def get_development_settings() -> Settings:
    """Get settings for development environment"""
    return Settings(
        ENVIRONMENT="development",
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        CONFIDENCE_THRESHOLD=0.6,  # Lower threshold for testing
        API_KEY="dev-api-key-12345",
        ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
    )

def get_staging_settings() -> Settings:
    """Get settings for staging environment"""
    return Settings(
        ENVIRONMENT="staging",
        DEBUG=False,
        LOG_LEVEL="INFO",
        CONFIDENCE_THRESHOLD=0.7,
        ALLOWED_ORIGINS=["https://staging.yourcompany.com"]
    )

def get_production_settings() -> Settings:
    """Get settings for production environment"""
    return Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        LOG_LEVEL="WARNING",
        CONFIDENCE_THRESHOLD=0.8,  # Higher threshold for production
        ALLOWED_ORIGINS=["https://www.yourcompany.com"]
    )

def get_settings() -> Settings:
    """
    Get settings based on environment
    
    This function automatically detects the environment and returns
    the appropriate settings configuration.
    """
    env = os.getenv("CHATBOT_ENVIRONMENT", "development").lower()
    
    if env == "production":
        return get_production_settings()
    elif env == "staging":
        return get_staging_settings()
    else:
        return get_development_settings()


# Example usage and testing
if __name__ == "__main__":
    # Test settings loading
    settings = get_settings()
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}")
    print(f"Supported Intents: {list(settings.INTENT_PATTERNS.keys())}")
