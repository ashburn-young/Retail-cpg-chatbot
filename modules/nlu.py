"""
Natural Language Understanding (NLU) Module
===========================================

This module handles natural language understanding for the retail & CPG chatbot.
It processes customer messages to extract intents and entities, enabling the chatbot
to understand what customers are asking about.

Features:
- Intent classification for retail/CPG domain
- Entity extraction (order numbers, product names, quantities, etc.)
- Confidence scoring
- Fallback handling for unknown intents
- Support for multiple languages (extensible)

Dependencies:
- spaCy for NLP processing
- Custom pattern matching for retail-specific terms
- Machine learning models for intent classification
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

import spacy
from spacy.matcher import Matcher
from spacy.util import filter_spans

from config.settings import Settings

logger = logging.getLogger(__name__)


class NLUProcessor:
    """
    Natural Language Understanding processor for retail and CPG customer service
    
    This class handles:
    - Loading and initializing NLP models
    - Intent classification based on customer messages
    - Entity extraction (products, order numbers, quantities, etc.)
    - Confidence scoring for predictions
    - Pattern matching for retail-specific terminology
    """
    
    def __init__(self, settings: Settings):
        """Initialize NLU processor with settings"""
        self.settings = settings
        self.nlp = None
        self.matcher = None
        self.intent_patterns = settings.INTENT_PATTERNS
        self.initialized = False
        
        # Retail-specific entity patterns
        self.entity_patterns = {
            "ORDER_NUMBER": [
                r"\b(?:order|order number|order #)\s*[:\-]?\s*([A-Z0-9]{6,20})\b",
                r"\b([A-Z]{2}\d{8,12})\b",  # Order number patterns
                r"\b(\d{10,15})\b"  # Numeric order IDs
            ],
            "PRODUCT_NAME": [
                r"\b(?:product|item)\s+(.+?)(?:\s+(?:in|at|for|with)|\.|$)",
                r"\"([^\"]+)\"",  # Quoted product names
                r"'([^']+)'"     # Single-quoted product names
            ],
            "QUANTITY": [
                r"\b(\d+)\s*(?:pcs?|pieces?|items?|units?|boxes?|cases?)\b",
                r"\b(?:quantity|qty)\s*[:\-]?\s*(\d+)\b"
            ],
            "PRICE_RANGE": [
                r"\$(\d+(?:\.\d{2})?)\s*(?:to|-)\s*\$(\d+(?:\.\d{2})?)",
                r"(?:under|below|less than)\s*\$(\d+(?:\.\d{2})?)",
                r"(?:over|above|more than)\s*\$(\d+(?:\.\d{2})?)"
            ],
            "STORE_LOCATION": [
                r"\b([A-Z]{2})\s+(\d{5}(?:-\d{4})?)\b",  # State + ZIP
                r"\b(\d{5}(?:-\d{4})?)\b",  # ZIP code
                r"\b(downtown|mall|center|plaza)\b"
            ]
        }
        
        # Intent keywords for pattern matching
        self.intent_keywords = {
            "track_order": [
                "track", "status", "where", "shipped", "delivery", "arrived",
                "order", "tracking", "shipment", "package"
            ],
            "product_info": [
                "information", "details", "about", "specifications", "specs",
                "ingredients", "nutrition", "features", "description"
            ],
            "inventory_check": [
                "stock", "available", "inventory", "in stock", "out of stock",
                "availability", "supply", "quantity"
            ],
            "store_locator": [
                "store", "location", "address", "hours", "phone", "contact",
                "nearest", "closest", "find", "where"
            ],
            "pricing": [
                "price", "cost", "expensive", "cheap", "discount", "sale",
                "promotion", "deal", "offer", "how much"
            ],
            "complaint": [
                "complaint", "problem", "issue", "broken", "damaged", "defective",
                "wrong", "mistake", "error", "unhappy", "disappointed"
            ],
            "shipping_info": [
                "shipping", "delivery", "freight", "overnight", "express",
                "standard", "shipping cost", "delivery time"
            ],
            "account_help": [
                "account", "login", "password", "profile", "register",
                "sign up", "username", "email"
            ]
        }
    
    async def initialize(self):
        """Initialize the NLU processor"""
        try:
            logger.info("Initializing NLU processor...")
            
            # Load spaCy model
            try:
                self.nlp = spacy.load(self.settings.NLU_MODEL_PATH)
                logger.info(f"Loaded spaCy model: {self.settings.NLU_MODEL_PATH}")
            except OSError:
                logger.warning(f"Could not load {self.settings.NLU_MODEL_PATH}, using en_core_web_sm")
                self.nlp = spacy.load("en_core_web_sm")
            
            # Initialize matcher for pattern-based entity extraction
            self.matcher = Matcher(self.nlp.vocab)
            self._setup_patterns()
            
            self.initialized = True
            logger.info("✅ NLU processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize NLU processor: {str(e)}")
            raise
    
    def _setup_patterns(self):
        """Setup pattern matching rules for entity extraction"""
        try:
            # Order number patterns
            order_patterns = [
                [{"TEXT": {"REGEX": r"^[A-Z]{2}\d{8,12}$"}}],  # Order format: AB12345678
                [{"LOWER": "order"}, {"TEXT": {"REGEX": r"^\d{8,15}$"}}],  # "order 123456789"
                [{"TEXT": "#"}, {"TEXT": {"REGEX": r"^[A-Z0-9]{6,20}$"}}]   # "#ABC123"
            ]
            
            # Product mention patterns
            product_patterns = [
                [{"LOWER": "product"}, {"POS": "NOUN"}],
                [{"LOWER": "item"}, {"POS": "NOUN"}],
                [{"TEXT": {"REGEX": r"^[A-Z][a-z]+\s[A-Z][a-z]+$"}}]  # Brand Name
            ]
            
            # Add patterns to matcher
            self.matcher.add("ORDER_NUMBER", order_patterns)
            self.matcher.add("PRODUCT_MENTION", product_patterns)
            
            logger.info("Pattern matching rules setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up patterns: {str(e)}")
    
    async def process(self, message: str) -> Dict[str, Any]:
        """
        Process a customer message and extract intent and entities
        
        Args:
            message: Customer message text
            
        Returns:
            Dictionary containing:
            - intent: Predicted intent
            - confidence: Confidence score (0-1)
            - entities: Extracted entities
            - processed_message: Cleaned message text
        """
        if not self.initialized:
            raise RuntimeError("NLU processor not initialized")
        
        try:
            # Clean and preprocess message
            cleaned_message = self._preprocess_message(message)
            
            # Process with spaCy
            doc = self.nlp(cleaned_message)
            
            # Extract intent
            intent, confidence = self._classify_intent(cleaned_message, doc)
            
            # Extract entities
            entities = self._extract_entities(cleaned_message, doc)
            
            # Post-process results
            result = {
                "intent": intent,
                "confidence": confidence,
                "entities": entities,
                "processed_message": cleaned_message,
                "original_message": message,
                "processing_time": datetime.now().isoformat()
            }
            
            logger.debug(f"NLU processing result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "intent": "error",
                "confidence": 0.0,
                "entities": {},
                "processed_message": message,
                "original_message": message,
                "error": str(e)
            }
    
    def _preprocess_message(self, message: str) -> str:
        """Clean and preprocess the message"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', message.strip())
        
        # Convert to lowercase for processing (but keep original case for entities)
        cleaned = cleaned.lower()
        
        # Remove special characters that don't add meaning
        cleaned = re.sub(r'[^\w\s\-#$.,!?]', ' ', cleaned)
        
        return cleaned
    
    def _classify_intent(self, message: str, doc) -> Tuple[str, float]:
        """
        Classify the intent of the message
        
        Returns:
            Tuple of (intent, confidence_score)
        """
        intent_scores = {}
        
        # Method 1: Keyword-based classification
        for intent, keywords in self.intent_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in message:
                    score += 1
            
            if score > 0:
                # Normalize score by number of keywords
                intent_scores[intent] = score / len(keywords)
        
        # Method 2: Pattern-based classification using configured patterns
        for intent, patterns in self.intent_patterns.items():
            pattern_score = 0
            for pattern in patterns:
                if pattern.lower() in message:
                    pattern_score += 1
            
            if pattern_score > 0:
                # Combine with existing score or set new score
                current_score = intent_scores.get(intent, 0)
                intent_scores[intent] = max(current_score, pattern_score / len(patterns))
        
        # Method 3: NLP-based classification using entities and POS tags
        self._enhance_classification_with_nlp(doc, intent_scores, message)
        
        # Determine best intent
        if not intent_scores:
            return "general_inquiry", 0.3
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[best_intent], 1.0)  # Cap at 1.0
        
        # Apply confidence adjustments
        confidence = self._adjust_confidence(best_intent, message, confidence)
        
        return best_intent, confidence
    
    def _enhance_classification_with_nlp(self, doc, intent_scores: Dict, message: str):
        """Enhance intent classification using NLP features"""
        
        # Check for question words
        question_words = ["what", "where", "when", "how", "why", "can", "could", "would"]
        has_question = any(token.text.lower() in question_words for token in doc)
        
        # Enhance specific intents based on NLP analysis
        entities = [ent.label_ for ent in doc.ents]
        
        # If we find money entities, boost pricing intent
        if "MONEY" in entities:
            intent_scores["pricing"] = intent_scores.get("pricing", 0) + 0.3
        
        # If we find numbers, might be order tracking
        if "CARDINAL" in entities and ("order" in message or "track" in message):
            intent_scores["track_order"] = intent_scores.get("track_order", 0) + 0.4
        
        # If we find product/organization entities
        if "PRODUCT" in entities or "ORG" in entities:
            intent_scores["product_info"] = intent_scores.get("product_info", 0) + 0.2
        
        # Location entities boost store locator
        if "GPE" in entities or "LOC" in entities:
            intent_scores["store_locator"] = intent_scores.get("store_locator", 0) + 0.3
    
    def _adjust_confidence(self, intent: str, message: str, base_confidence: float) -> float:
        """Adjust confidence based on various factors"""
        
        # Boost confidence for very clear indicators
        high_confidence_patterns = {
            "track_order": ["track my order", "order status", "where is my order"],
            "product_info": ["tell me about", "product information", "what is"],
            "inventory_check": ["in stock", "available", "out of stock"],
            "pricing": ["how much", "price of", "cost of"]
        }
        
        if intent in high_confidence_patterns:
            for pattern in high_confidence_patterns[intent]:
                if pattern in message:
                    base_confidence = min(base_confidence + 0.2, 1.0)
                    break
        
        # Reduce confidence for very short messages
        if len(message.split()) < 3:
            base_confidence *= 0.8
        
        # Reduce confidence for very long messages (might be complex)
        if len(message.split()) > 20:
            base_confidence *= 0.9
        
        return base_confidence
    
    def _extract_entities(self, message: str, doc) -> Dict[str, Any]:
        """Extract entities from the message"""
        entities = {}
        
        # Extract entities using spaCy NER
        for ent in doc.ents:
            entity_type = ent.label_
            entity_text = ent.text
            
            # Map spaCy entities to our domain
            if entity_type in ["CARDINAL", "ORDINAL"]:
                entities.setdefault("quantities", []).append(entity_text)
            elif entity_type == "MONEY":
                entities.setdefault("prices", []).append(entity_text)
            elif entity_type in ["GPE", "LOC"]:
                entities.setdefault("locations", []).append(entity_text)
            elif entity_type in ["PRODUCT", "ORG"]:
                entities.setdefault("products", []).append(entity_text)
            elif entity_type == "DATE":
                entities.setdefault("dates", []).append(entity_text)
        
        # Extract using custom patterns
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, message, re.IGNORECASE)
                if found:
                    matches.extend(found)
            
            if matches:
                entities[entity_type.lower()] = matches
        
        # Extract using spaCy matcher
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            label = self.nlp.vocab.strings[match_id]
            entities.setdefault(label.lower(), []).append(span.text)
        
        return entities
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents"""
        return list(self.intent_patterns.keys())
    
    def get_intent_description(self, intent: str) -> str:
        """Get description for a specific intent"""
        descriptions = {
            "track_order": "Customer wants to track their order status",
            "product_info": "Customer needs information about a product",
            "inventory_check": "Customer wants to check product availability",
            "store_locator": "Customer is looking for store information",
            "pricing": "Customer is asking about product prices",
            "complaint": "Customer has a complaint or issue",
            "shipping_info": "Customer needs shipping/delivery information",
            "account_help": "Customer needs help with their account",
            "general_inquiry": "General customer inquiry"
        }
        return descriptions.get(intent, "Unknown intent")
    
    async def batch_process(self, messages: List[str]) -> List[Dict[str, Any]]:
        """Process multiple messages in batch"""
        results = []
        for message in messages:
            result = await self.process(message)
            results.append(result)
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "model_name": self.nlp.meta.get("name", "unknown") if self.nlp else "not_loaded",
            "supported_intents": len(self.intent_patterns),
            "entity_patterns": len(self.entity_patterns),
            "initialized": self.initialized
        }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from config.settings import Settings
    
    async def test_nlu():
        """Test the NLU processor"""
        settings = Settings()
        nlu = NLUProcessor(settings)
        await nlu.initialize()
        
        test_messages = [
            "I want to track my order AB12345678",
            "What's the price of organic bananas?",
            "Is the iPhone 13 in stock?",
            "Where is your nearest store?",
            "I have a complaint about my recent purchase",
            "Can you help me with my account login?"
        ]
        
        print("Testing NLU Processor")
        print("=" * 50)
        
        for message in test_messages:
            result = await nlu.process(message)
            print(f"\nMessage: {message}")
            print(f"Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
            print(f"Entities: {result['entities']}")
        
        print(f"\nSupported intents: {nlu.get_supported_intents()}")
    
    # Run test
    asyncio.run(test_nlu())
