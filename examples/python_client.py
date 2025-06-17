#!/usr/bin/env python3
"""
Python Client Example for Retail & CPG Customer Service Chatbot
===============================================================

This script demonstrates how to interact with the chatbot API programmatically.
It can be used for testing, integration, or building custom interfaces.

Usage:
    python python_client.py
    python python_client.py --interactive
    python python_client.py --test-scenarios
"""

import asyncio
import aiohttp
import json
import uuid
import argparse
import time
from typing import Dict, Any, Optional
from datetime import datetime


class ChatbotClient:
    """
    Async client for the Retail & CPG Customer Service Chatbot API
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: str = "your-api-key-here",
    ):
        """
        Initialize the chatbot client

        Args:
            base_url: The base URL of the chatbot API
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session_id = f"python-client-{uuid.uuid4()}"
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=aiohttp.ClientTimeout(total=30),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health status of the chatbot API

        Returns:
            Health status response
        """
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return {
                    "status_code": response.status,
                    "data": await response.json() if response.status == 200 else None,
                    "error": None,
                }
        except Exception as e:
            return {"status_code": 0, "data": None, "error": str(e)}

    async def send_message(
        self, message: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send a message to the chatbot

        Args:
            message: The user message
            context: Optional context information

        Returns:
            Chatbot response
        """
        payload = {"message": message, "session_id": self.session_id}

        if context:
            payload["context"] = context

        try:
            async with self.session.post(
                f"{self.base_url}/chat", json=payload
            ) as response:
                response_data = await response.json()
                return {
                    "status_code": response.status,
                    "data": response_data,
                    "error": None,
                }
        except Exception as e:
            return {"status_code": 0, "data": None, "error": str(e)}

    async def get_context(self) -> Dict[str, Any]:
        """
        Get the current conversation context

        Returns:
            Context information
        """
        try:
            async with self.session.get(
                f"{self.base_url}/context/{self.session_id}"
            ) as response:
                return {
                    "status_code": response.status,
                    "data": await response.json() if response.status == 200 else None,
                    "error": None,
                }
        except Exception as e:
            return {"status_code": 0, "data": None, "error": str(e)}

    async def get_analytics(self) -> Dict[str, Any]:
        """
        Get analytics data

        Returns:
            Analytics information
        """
        try:
            async with self.session.get(f"{self.base_url}/analytics") as response:
                return {
                    "status_code": response.status,
                    "data": await response.json() if response.status == 200 else None,
                    "error": None,
                }
        except Exception as e:
            return {"status_code": 0, "data": None, "error": str(e)}

    async def clear_context(self) -> Dict[str, Any]:
        """
        Clear the conversation context

        Returns:
            Clear operation result
        """
        try:
            async with self.session.delete(
                f"{self.base_url}/context/{self.session_id}"
            ) as response:
                return {
                    "status_code": response.status,
                    "data": await response.json() if response.status == 200 else None,
                    "error": None,
                }
        except Exception as e:
            return {"status_code": 0, "data": None, "error": str(e)}


async def interactive_mode(client: ChatbotClient):
    """
    Run the client in interactive mode
    """
    print("🛍️ Retail & CPG Customer Service Chatbot - Python Client")
    print("=" * 60)
    print("Session ID:", client.session_id)
    print("Type 'quit' to exit, 'clear' to clear context, 'context' to view context")
    print("=" * 60)

    # Check health
    health = await client.health_check()
    if health["status_code"] == 200:
        print("✅ Connected to chatbot successfully!")
    else:
        print(f"❌ Failed to connect: {health['error']}")
        return

    print("\n👋 You can start chatting now!\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "quit":
                print("👋 Goodbye!")
                break

            if user_input.lower() == "clear":
                result = await client.clear_context()
                if result["status_code"] == 200:
                    print("🧹 Context cleared successfully!")
                else:
                    print(f"❌ Failed to clear context: {result['error']}")
                continue

            if user_input.lower() == "context":
                result = await client.get_context()
                if result["status_code"] == 200:
                    print(f"📋 Context: {json.dumps(result['data'], indent=2)}")
                else:
                    print(f"❌ Failed to get context: {result['error']}")
                continue

            # Send message
            print("🤖 Assistant is typing...")
            start_time = time.time()

            response = await client.send_message(user_input)
            response_time = (time.time() - start_time) * 1000

            if response["status_code"] == 200:
                data = response["data"]
                print(f"Bot: {data['response']}")
                print(
                    f"     (Intent: {data.get('intent', 'unknown')}, "
                    f"Confidence: {data.get('confidence', 0):.2f}, "
                    f"Response time: {response_time:.0f}ms)"
                )

                # Show escalation notice if needed
                if data.get("escalation_needed"):
                    print("⚠️  This conversation has been flagged for human escalation")
            else:
                print(f"❌ Error: {response['error']}")

            print()  # Empty line for readability

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


async def test_scenarios(client: ChatbotClient):
    """
    Run predefined test scenarios
    """
    print("🧪 Running Test Scenarios")
    print("=" * 30)

    # Health check
    print("1. Health Check...")
    health = await client.health_check()
    print(f"   Status: {'✅ OK' if health['status_code'] == 200 else '❌ Failed'}")

    if health["status_code"] != 200:
        print("   Cannot continue testing - chatbot is not available")
        return

    # Test scenarios
    scenarios = [
        {
            "name": "Order Tracking",
            "message": "I want to track my order AB12345678",
            "expected_intent": "track_order",
        },
        {
            "name": "Product Information",
            "message": "Tell me about the iPhone 15 Pro",
            "expected_intent": "product_info",
        },
        {
            "name": "Inventory Check",
            "message": "Is the MacBook Pro in stock?",
            "expected_intent": "inventory_check",
        },
        {
            "name": "Store Locator",
            "message": "Find stores near me in New York",
            "expected_intent": "store_locator",
        },
        {
            "name": "Complaint",
            "message": "I am not satisfied with my recent purchase",
            "expected_intent": "complaint",
        },
        {"name": "Greeting", "message": "Hello there!", "expected_intent": "greeting"},
        {
            "name": "Unclear Intent",
            "message": "xyz random text that makes no sense",
            "expected_intent": "unknown",
        },
    ]

    results = []

    for i, scenario in enumerate(scenarios, 2):
        print(f"\n{i}. Testing: {scenario['name']}")
        print(f"   Message: \"{scenario['message']}\"")

        start_time = time.time()
        response = await client.send_message(scenario["message"])
        response_time = (time.time() - start_time) * 1000

        if response["status_code"] == 200:
            data = response["data"]
            intent = data.get("intent", "unknown")
            confidence = data.get("confidence", 0)

            # Check if intent matches expected
            intent_correct = intent == scenario["expected_intent"]

            print(
                f"   Response: \"{data['response'][:100]}{'...' if len(data['response']) > 100 else ''}\""
            )
            print(f"   Intent: {intent} {'✅' if intent_correct else '❌'}")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   Response Time: {response_time:.0f}ms")

            results.append(
                {
                    "scenario": scenario["name"],
                    "success": True,
                    "intent_correct": intent_correct,
                    "confidence": confidence,
                    "response_time": response_time,
                }
            )
        else:
            print(f"   ❌ Failed: {response['error']}")
            results.append(
                {
                    "scenario": scenario["name"],
                    "success": False,
                    "intent_correct": False,
                    "confidence": 0,
                    "response_time": 0,
                }
            )

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)

    successful_tests = sum(1 for r in results if r["success"])
    correct_intents = sum(1 for r in results if r["intent_correct"])
    avg_response_time = sum(r["response_time"] for r in results if r["success"]) / max(
        1, successful_tests
    )
    avg_confidence = sum(r["confidence"] for r in results if r["success"]) / max(
        1, successful_tests
    )

    print(f"Total Tests: {len(results)}")
    print(
        f"Successful: {successful_tests}/{len(results)} ({successful_tests/len(results)*100:.1f}%)"
    )
    print(
        f"Correct Intents: {correct_intents}/{len(results)} ({correct_intents/len(results)*100:.1f}%)"
    )
    print(f"Average Response Time: {avg_response_time:.0f}ms")
    print(f"Average Confidence: {avg_confidence:.2f}")

    # Show analytics
    print("\n📈 Getting Analytics...")
    analytics = await client.get_analytics()
    if analytics["status_code"] == 200:
        print(f"Analytics: {json.dumps(analytics['data'], indent=2)}")
    else:
        print(f"❌ Failed to get analytics: {analytics['error']}")


async def simple_test(client: ChatbotClient):
    """
    Run a simple connectivity test
    """
    print("🔍 Simple Connectivity Test")
    print("=" * 30)

    # Health check
    health = await client.health_check()
    print(f"Health Check: {'✅ OK' if health['status_code'] == 200 else '❌ Failed'}")

    if health["status_code"] == 200:
        # Send a simple message
        response = await client.send_message("Hello!")
        if response["status_code"] == 200:
            print(f"Chat Test: ✅ OK")
            print(f"Response: {response['data']['response']}")
        else:
            print(f"Chat Test: ❌ Failed - {response['error']}")

    print("Test completed!")


async def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description="Retail & CPG Chatbot Python Client")
    parser.add_argument(
        "--url", default="http://localhost:8000", help="Chatbot API URL"
    )
    parser.add_argument("--api-key", default="your-api-key-here", help="API key")
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive mode"
    )
    parser.add_argument(
        "--test-scenarios", action="store_true", help="Run test scenarios"
    )
    parser.add_argument(
        "--simple-test", action="store_true", help="Run simple connectivity test"
    )

    args = parser.parse_args()

    # Create client
    async with ChatbotClient(args.url, args.api_key) as client:
        if args.interactive:
            await interactive_mode(client)
        elif args.test_scenarios:
            await test_scenarios(client)
        elif args.simple_test:
            await simple_test(client)
        else:
            # Default: run interactive mode
            await interactive_mode(client)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
