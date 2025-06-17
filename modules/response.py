"""
Response Generation Module
=========================

This module handles dynamic response generation for the retail & CPG chatbot.
It creates contextual, personalized responses based on customer intents, entities,
conversation history, and backend data.

Features:
- Template-based response generation with dynamic placeholders
- Context-aware responses using conversation history
- Personalization based on customer data
- Escalation handling for complex scenarios
- Multi-turn conversation support
- A/B testing capability for response optimization
"""

import re
import logging
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from string import Template

from config.settings import Settings

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generates dynamic, contextual responses for customer service interactions
    
    This class handles:
    - Template-based response generation
    - Dynamic placeholder replacement
    - Context-aware response selection
    - Escalation logic
    - Personalization based on customer data
    - Response variation to avoid repetition
    """
    
    def __init__(self, settings: Settings):
        """Initialize response generator with settings"""
        self.settings = settings
        self.response_templates = settings.RESPONSE_TEMPLATES
        self.escalation_keywords = settings.ESCALATION_KEYWORDS
        
        # Extended response templates for better conversation flow
        self.extended_templates = {
            # Greeting responses
            "greeting": [
                "Hello! I'm here to help you with your questions about our products and services. What can I assist you with today?",
                "Hi there! Welcome to {company_name}. How can I help you today?",
                "Good day! I'm your virtual assistant for {company_name}. What would you like to know?"
            ],
            
            # Order tracking responses
            "track_order": [
                "I'd be happy to help you track your order! {order_info}",
                "Let me look up your order details for you. {order_info}",
                "Here's the latest information about your order: {order_info}"
            ],
            
            "order_found": [
                "Great! I found your order {order_number}. It's currently {status}. {additional_info}",
                "Your order {order_number} is {status}. {additional_info}",
                "Order {order_number} status: {status}. {additional_info}"
            ],
            
            "order_not_found": [
                "I'm sorry, I couldn't find an order with that number. Could you please double-check the order number?",
                "I don't see an order matching that number in our system. Please verify the order number and try again.",
                "That order number doesn't appear in our records. Can you please confirm the correct order number?"
            ],
            
            # Product information responses
            "product_info": [
                "Here's what I can tell you about {product_name}: {product_details}",
                "Let me share the details about {product_name}: {product_details}",
                "I'd be happy to provide information about {product_name}: {product_details}"
            ],
            
            "product_not_found": [
                "I couldn't find information about that specific product. Could you provide more details or check the spelling?",
                "I don't have details on that product in our catalog. Can you describe it differently?",
                "That product doesn't appear in our current inventory. Would you like me to suggest similar items?"
            ],
            
            # Inventory responses
            "inventory_check": [
                "Let me check availability for {product_name}. {stock_info}",
                "Here's the current stock status for {product_name}: {stock_info}",
                "I've checked our inventory for {product_name}. {stock_info}"
            ],
            
            "in_stock": [
                "Great news! {product_name} is currently in stock. {quantity_info}",
                "Yes, we have {product_name} available right now. {quantity_info}",
                "{product_name} is in stock and ready to ship. {quantity_info}"
            ],
            
            "out_of_stock": [
                "I'm sorry, {product_name} is currently out of stock. {restock_info}",
                "Unfortunately, {product_name} is not available right now. {restock_info}",
                "{product_name} is temporarily out of stock. {restock_info}"
            ],
            
            # Store locator responses
            "store_locator": [
                "I found {store_count} stores near you. {store_info}",
                "Here are the closest store locations: {store_info}",
                "Based on your location, here are nearby stores: {store_info}"
            ],
            
            # Pricing responses
            "pricing": [
                "The current price for {product_name} is {price}. {promotion_info}",
                "Here's the pricing information for {product_name}: {price}. {promotion_info}",
                "{product_name} is priced at {price}. {promotion_info}"
            ],
            
            # Complaint handling
            "complaint_acknowledgment": [
                "I understand your concern and I'm sorry you're experiencing this issue. Let me help you resolve it.",
                "I apologize for the inconvenience you've experienced. I'm here to help make this right.",
                "Thank you for bringing this to my attention. I want to ensure we address your concern properly."
            ],
            
            # Escalation responses
            "escalation": [
                "I'd like to connect you with one of our customer service specialists who can provide more detailed assistance. Please hold while I transfer you.",
                "Let me get you connected with a human agent who can better help with your specific situation.",
                "I think our customer service team would be better equipped to handle this for you. Let me transfer you now."
            ],
            
            # Fallback responses
            "fallback": [
                "I'm not sure I fully understand. Could you please rephrase your question?",
                "I didn't quite catch that. Can you tell me more about what you're looking for?",
                "I want to make sure I help you with the right information. Could you be more specific about your question?"
            ],
            
            # Clarification requests
            "clarification": [
                "To help you better, could you provide more details about {topic}?",
                "I want to make sure I give you the right information. Can you tell me more about {topic}?",
                "Could you help me understand what specifically you'd like to know about {topic}?"
            ],
            
            # Positive responses
            "positive": [
                "Excellent! Is there anything else I can help you with today?",
                "Great! I'm glad I could help. Do you have any other questions?",
                "Perfect! Feel free to ask if you need anything else."
            ],
            
            # Error responses
            "error": [
                "I apologize, but I'm having trouble accessing that information right now. Please try again in a moment.",
                "I'm experiencing a technical issue at the moment. Could you please try your request again?",
                "I'm sorry, there seems to be a temporary problem. Please try again or speak with a human agent."
            ]
        }
        
        # Response modifiers for personalization
        self.response_modifiers = {
            "polite": ["please", "kindly", "if you don't mind"],
            "urgent": ["immediately", "right away", "as soon as possible"],
            "friendly": ["absolutely", "definitely", "of course"],
            "apologetic": ["I apologize", "I'm sorry", "unfortunately"]
        }
        
        # Context-based response adjustments
        self.context_adjustments = {
            "repeat_customer": "Thank you for being a valued customer! ",
            "first_time": "Welcome to {company_name}! ",
            "frustrated": "I understand this can be frustrating. ",
            "satisfied": "I'm glad I could help! "
        }
    
    async def generate_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        backend_data: Dict[str, Any] = None,
        confidence: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate a contextual response based on intent, entities, and context
        
        Args:
            intent: Detected customer intent
            entities: Extracted entities from the message
            context: Conversation context and history
            backend_data: Data from backend systems
            confidence: Confidence score of the intent detection
            
        Returns:
            Dictionary containing response text and metadata
        """
        try:
            logger.debug(f"Generating response for intent: {intent}")
            
            # Determine response strategy based on intent and confidence
            if confidence < self.settings.CONFIDENCE_THRESHOLD:
                return await self._generate_clarification_response(intent, entities, context)
            
            # Check for escalation triggers
            if self._should_escalate(intent, entities, context):
                return await self._generate_escalation_response(context)
            
            # Generate main response based on intent
            response_data = await self._generate_intent_response(
                intent, entities, context, backend_data
            )
            
            # Apply personalization and context adjustments
            response_data = self._apply_personalization(response_data, context)
            
            # Add suggested actions
            response_data["suggested_actions"] = self._generate_suggested_actions(
                intent, entities, context
            )
            
            # Determine if escalation is needed
            response_data["escalate_to_human"] = self._should_escalate(intent, entities, context)
            
            logger.debug(f"Generated response: {response_data['response'][:100]}...")
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "response": self._get_error_response(),
                "escalate_to_human": True,
                "suggested_actions": ["speak_with_agent"],
                "error": str(e)
            }
    
    async def _generate_intent_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        backend_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate response for specific intent"""
        
        if intent == "track_order":
            return await self._handle_order_tracking(entities, context, backend_data)
        elif intent == "product_info":
            return await self._handle_product_info(entities, context, backend_data)
        elif intent == "inventory_check":
            return await self._handle_inventory_check(entities, context, backend_data)
        elif intent == "store_locator":
            return await self._handle_store_locator(entities, context, backend_data)
        elif intent == "pricing":
            return await self._handle_pricing(entities, context, backend_data)
        elif intent == "complaint":
            return await self._handle_complaint(entities, context, backend_data)
        elif intent == "shipping_info":
            return await self._handle_shipping_info(entities, context, backend_data)
        elif intent == "account_help":
            return await self._handle_account_help(entities, context, backend_data)
        else:
            return await self._handle_general_inquiry(entities, context, backend_data)
    
    async def _handle_order_tracking(self, entities, context, backend_data):
        """Handle order tracking requests"""
        order_numbers = entities.get("order_number", [])
        
        if backend_data and "order_info" in backend_data:
            order_info = backend_data["order_info"]
            if order_info.get("found"):
                template = self._get_random_template("order_found")
                response = template.format(
                    order_number=order_info.get("order_number", ""),
                    status=order_info.get("status", "unknown"),
                    additional_info=order_info.get("additional_info", "")
                )
            else:
                response = self._get_random_template("order_not_found")
        else:
            if order_numbers:
                template = self._get_random_template("track_order")
                response = template.format(
                    order_info=f"I'm looking up order {order_numbers[0]} for you..."
                )
            else:
                response = "I'd be happy to help you track your order. Could you please provide your order number?"
        
        return {"response": response}
    
    async def _handle_product_info(self, entities, context, backend_data):
        """Handle product information requests"""
        products = entities.get("products", []) or entities.get("product_mention", [])
        
        if backend_data and "product_info" in backend_data:
            product_info = backend_data["product_info"]
            if product_info.get("found"):
                template = self._get_random_template("product_info")
                response = template.format(
                    product_name=product_info.get("name", "the product"),
                    product_details=product_info.get("details", "Information not available")
                )
            else:
                response = self._get_random_template("product_not_found")
        else:
            if products:
                template = self._get_random_template("product_info")
                response = template.format(
                    product_name=products[0],
                    product_details="Let me gather that information for you..."
                )
            else:
                response = "I'd be happy to help you with product information. Which product are you interested in?"
        
        return {"response": response}
    
    async def _handle_inventory_check(self, entities, context, backend_data):
        """Handle inventory availability requests"""
        products = entities.get("products", []) or entities.get("product_mention", [])
        
        if backend_data and "inventory_info" in backend_data:
            inventory = backend_data["inventory_info"]
            product_name = inventory.get("product_name", "the product")
            
            if inventory.get("in_stock"):
                template = self._get_random_template("in_stock")
                quantity_info = ""
                if inventory.get("quantity"):
                    quantity_info = f"We have {inventory['quantity']} units available."
                response = template.format(
                    product_name=product_name,
                    quantity_info=quantity_info
                )
            else:
                template = self._get_random_template("out_of_stock")
                restock_info = inventory.get("restock_date", "We'll notify you when it's back in stock.")
                response = template.format(
                    product_name=product_name,
                    restock_info=restock_info
                )
        else:
            if products:
                template = self._get_random_template("inventory_check")
                response = template.format(
                    product_name=products[0],
                    stock_info="Let me check our current inventory..."
                )
            else:
                response = "I can check product availability for you. Which product would you like me to look up?"
        
        return {"response": response}
    
    async def _handle_store_locator(self, entities, context, backend_data):
        """Handle store location requests"""
        locations = entities.get("locations", []) or entities.get("store_location", [])
        
        if backend_data and "stores" in backend_data:
            stores = backend_data["stores"]
            store_count = len(stores)
            
            if store_count > 0:
                store_info = self._format_store_list(stores[:3])  # Show top 3
                template = self._get_random_template("store_locator")
                response = template.format(
                    store_count=store_count,
                    store_info=store_info
                )
            else:
                response = "I couldn't find any stores in that area. Could you try a different location?"
        else:
            response = "I'd be happy to help you find our store locations. What area are you looking in?"
        
        return {"response": response}
    
    async def _handle_pricing(self, entities, context, backend_data):
        """Handle pricing information requests"""
        products = entities.get("products", [])
        prices = entities.get("prices", [])
        
        if backend_data and "pricing_info" in backend_data:
            pricing = backend_data["pricing_info"]
            template = self._get_random_template("pricing")
            promotion_info = ""
            if pricing.get("promotion"):
                promotion_info = f"Currently on sale: {pricing['promotion']}"
            
            response = template.format(
                product_name=pricing.get("product_name", "the product"),
                price=pricing.get("price", "Price not available"),
                promotion_info=promotion_info
            )
        else:
            if products:
                response = f"Let me get the current pricing information for {products[0]}..."
            else:
                response = "I can help you with pricing information. Which product are you interested in?"
        
        return {"response": response}
    
    async def _handle_complaint(self, entities, context, backend_data):
        """Handle customer complaints"""
        # Always show empathy for complaints
        template = self._get_random_template("complaint_acknowledgment")
        
        # Check if we have specific complaint handling data
        if backend_data and "complaint_info" in backend_data:
            complaint_data = backend_data["complaint_info"]
            additional_info = complaint_data.get("resolution_steps", "")
            if additional_info:
                template += f" {additional_info}"
        
        return {
            "response": template,
            "escalate_to_human": True  # Always consider escalating complaints
        }
    
    async def _handle_shipping_info(self, entities, context, backend_data):
        """Handle shipping and delivery inquiries"""
        if backend_data and "shipping_info" in backend_data:
            shipping = backend_data["shipping_info"]
            response = f"Here's the shipping information: {shipping.get('details', 'Standard shipping takes 3-5 business days.')}"
        else:
            response = "I can help you with shipping information. Are you asking about shipping costs, delivery times, or tracking a shipment?"
        
        return {"response": response}
    
    async def _handle_account_help(self, entities, context, backend_data):
        """Handle account-related requests"""
        response = "I can help you with account-related questions. For security reasons, I'll need to verify your identity first. Would you prefer to speak with a human agent for account assistance?"
        
        return {
            "response": response,
            "escalate_to_human": True  # Account issues often need human verification
        }
    
    async def _handle_general_inquiry(self, entities, context, backend_data):
        """Handle general inquiries"""
        template = self._get_random_template("fallback")
        return {"response": template}
    
    def _format_store_list(self, stores: List[Dict]) -> str:
        """Format a list of stores for display"""
        if not stores:
            return "No stores found."
        
        formatted = []
        for store in stores:
            store_text = f"{store.get('name', 'Store')} - {store.get('address', 'Address not available')}"
            if store.get('phone'):
                store_text += f" (Phone: {store['phone']})"
            formatted.append(store_text)
        
        return "\n".join(formatted)
    
    async def _generate_clarification_response(self, intent, entities, context):
        """Generate a clarification request when confidence is low"""
        topic_map = {
            "track_order": "order tracking",
            "product_info": "product information",
            "inventory_check": "product availability",
            "store_locator": "store locations",
            "pricing": "pricing information"
        }
        
        topic = topic_map.get(intent, "your question")
        template = self._get_random_template("clarification")
        response = template.format(topic=topic)
        
        return {
            "response": response,
            "escalate_to_human": False,
            "requires_clarification": True
        }
    
    async def _generate_escalation_response(self, context):
        """Generate escalation response"""
        template = self._get_random_template("escalation")
        return {
            "response": template,
            "escalate_to_human": True
        }
    
    def _should_escalate(self, intent, entities, context) -> bool:
        """Determine if the conversation should be escalated to a human"""
        
        # Always escalate complaints and account issues
        if intent in ["complaint", "account_help"]:
            return True
        
        # Check for escalation keywords in the conversation history
        conversation_text = " ".join([
            context.get("last_message", ""),
            context.get("conversation_history", "")
        ]).lower()
        
        for keyword in self.escalation_keywords:
            if keyword in conversation_text:
                return True
        
        # Escalate if customer has been in conversation for too long
        turn_count = context.get("turn_count", 0)
        if turn_count > 5:  # More than 5 exchanges
            return True
        
        return False
    
    def _generate_suggested_actions(self, intent, entities, context) -> List[str]:
        """Generate suggested follow-up actions"""
        suggestions = {
            "track_order": ["check_delivery_address", "contact_shipping_carrier"],
            "product_info": ["view_similar_products", "read_reviews", "check_availability"],
            "inventory_check": ["notify_when_available", "find_similar_products"],
            "store_locator": ["get_directions", "call_store", "check_store_hours"],
            "pricing": ["view_promotions", "compare_products", "add_to_cart"],
            "complaint": ["speak_with_manager", "file_formal_complaint"],
            "shipping_info": ["track_package", "change_delivery_address"],
            "account_help": ["reset_password", "speak_with_agent"]
        }
        
        return suggestions.get(intent, ["speak_with_agent"])
    
    def _apply_personalization(self, response_data, context) -> Dict[str, Any]:
        """Apply personalization based on customer context"""
        response = response_data.get("response", "")
        
        # Add context-based prefixes
        customer_type = context.get("customer_type", "")
        if customer_type in self.context_adjustments:
            prefix = self.context_adjustments[customer_type].format(
                company_name=self.settings.COMPANY_NAME
            )
            response = prefix + response
        
        # Replace company-specific placeholders
        response = response.replace("{company_name}", self.settings.COMPANY_NAME)
        response = response.replace("{support_email}", self.settings.SUPPORT_EMAIL)
        response = response.replace("{support_phone}", self.settings.SUPPORT_PHONE)
        
        response_data["response"] = response
        return response_data
    
    def _get_random_template(self, template_key: str) -> str:
        """Get a random template for variety"""
        templates = self.extended_templates.get(template_key, [])
        if not templates:
            return self.response_templates.get(template_key, "I'm here to help!")
        
        return random.choice(templates)
    
    def _get_error_response(self) -> str:
        """Get a random error response"""
        return self._get_random_template("error")
    
    def get_escalation_message(self) -> str:
        """Get escalation message"""
        return self._get_random_template("escalation")
    
    def get_response_templates(self) -> Dict[str, Any]:
        """Get all available response templates"""
        return {
            "basic": self.response_templates,
            "extended": self.extended_templates
        }


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from config.settings import Settings
    
    async def test_response_generator():
        """Test the response generator"""
        settings = Settings()
        generator = ResponseGenerator(settings)
        
        # Test scenarios
        test_cases = [
            {
                "intent": "track_order",
                "entities": {"order_number": ["AB12345678"]},
                "context": {"customer_type": "repeat_customer"},
                "backend_data": {
                    "order_info": {
                        "found": True,
                        "order_number": "AB12345678",
                        "status": "shipped",
                        "additional_info": "Expected delivery: Tomorrow"
                    }
                }
            },
            {
                "intent": "product_info",
                "entities": {"products": ["iPhone 13"]},
                "context": {"customer_type": "first_time"},
                "backend_data": {
                    "product_info": {
                        "found": True,
                        "name": "iPhone 13",
                        "details": "Latest Apple smartphone with A15 Bionic chip"
                    }
                }
            },
            {
                "intent": "complaint",
                "entities": {},
                "context": {"customer_type": "frustrated"},
                "backend_data": {}
            }
        ]
        
        print("Testing Response Generator")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"Intent: {test_case['intent']}")
            
            response = await generator.generate_response(
                intent=test_case["intent"],
                entities=test_case["entities"],
                context=test_case["context"],
                backend_data=test_case["backend_data"]
            )
            
            print(f"Response: {response['response']}")
            print(f"Escalate: {response.get('escalate_to_human', False)}")
            print(f"Suggestions: {response.get('suggested_actions', [])}")
    
    # Run test
    asyncio.run(test_response_generator())
