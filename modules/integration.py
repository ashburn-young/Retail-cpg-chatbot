"""
Backend Integration Module
=========================

This module handles integration with external backend systems such as:
- Order Management Systems (OMS)
- Inventory Management Systems
- Product Information Systems
- Store Locator Services
- Customer Relationship Management (CRM)

Features:
- Async HTTP client for API calls
- Retry logic with exponential backoff
- Circuit breaker pattern for fault tolerance
- Response caching for performance
- Mock services for development and testing
- Secure API key management
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

import aiohttp
from aiohttp import ClientTimeout, ClientError

from config.settings import Settings

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


@dataclass
class APIResponse:
    """Standardized API response"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    cached: bool = False


class CircuitBreaker:
    """Circuit breaker for fault tolerance"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if datetime.now() - self.last_failure_time > timedelta(
                seconds=self.timeout
            ):
                self.state = "half-open"
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"

            raise e


class BaseService(ABC):
    """Base class for all backend services"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.circuit_breaker = CircuitBreaker()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Retail-CPG-Chatbot/1.0",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Generate cache key"""
        key = f"{self.base_url}{endpoint}"
        if params:
            key += f"?{json.dumps(params, sort_keys=True)}"
        return key

    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry:
            return False

        timestamp = cache_entry.get("timestamp")
        if not timestamp:
            return False

        return (datetime.now() - timestamp).seconds < self.cache_ttl

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True,
    ) -> APIResponse:
        """Make HTTP request with error handling and caching"""

        # Check cache first (for GET requests)
        if method.upper() == "GET" and use_cache:
            cache_key = self._get_cache_key(endpoint, params)
            cached_response = self.cache.get(cache_key)

            if self._is_cache_valid(cached_response):
                logger.debug(f"Cache hit for {endpoint}")
                return APIResponse(
                    success=True, data=cached_response["data"], cached=True
                )

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        timeout = ClientTimeout(total=10)  # 10 second timeout

        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=method, url=url, headers=headers, params=params, json=data
                ) as response:
                    response_time = (datetime.now() - start_time).total_seconds()

                    if response.status == 200:
                        response_data = await response.json()

                        # Cache successful GET responses
                        if method.upper() == "GET" and use_cache:
                            cache_key = self._get_cache_key(endpoint, params)
                            self.cache[cache_key] = {
                                "data": response_data,
                                "timestamp": datetime.now(),
                            }

                        return APIResponse(
                            success=True,
                            data=response_data,
                            status_code=response.status,
                            response_time=response_time,
                        )
                    else:
                        error_text = await response.text()
                        return APIResponse(
                            success=False,
                            error=f"HTTP {response.status}: {error_text}",
                            status_code=response.status,
                            response_time=response_time,
                        )

        except asyncio.TimeoutError:
            return APIResponse(
                success=False,
                error="Request timeout",
                response_time=(datetime.now() - start_time).total_seconds(),
            )
        except ClientError as e:
            return APIResponse(
                success=False,
                error=f"Client error: {str(e)}",
                response_time=(datetime.now() - start_time).total_seconds(),
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=f"Unexpected error: {str(e)}",
                response_time=(datetime.now() - start_time).total_seconds(),
            )

    @abstractmethod
    async def health_check(self) -> ServiceStatus:
        """Check service health"""
        pass


class OrderService(BaseService):
    """Order Management System integration"""

    async def get_order(
        self, order_number: str, customer_id: Optional[str] = None
    ) -> APIResponse:
        """Get order information by order number"""
        try:
            endpoint = f"/orders/{order_number}"
            params = {}

            if customer_id:
                params["customer_id"] = customer_id

            response = await self.circuit_breaker.call(
                self._make_request, "GET", endpoint, params
            )

            if response.success and response.data:
                # Transform response to standard format
                order_data = response.data

                transformed_data = {
                    "order_info": {
                        "found": True,
                        "order_number": order_data.get("order_number", order_number),
                        "status": order_data.get("status", "unknown"),
                        "additional_info": self._format_order_details(order_data),
                    }
                }

                return APIResponse(success=True, data=transformed_data)

            return APIResponse(
                success=True,
                data={"order_info": {"found": False}},
                error="Order not found",
            )

        except Exception as e:
            logger.error(f"Error getting order {order_number}: {str(e)}")
            return APIResponse(success=False, error=str(e))

    def _format_order_details(self, order_data: Dict) -> str:
        """Format order details for display"""
        details = []

        if order_data.get("estimated_delivery"):
            details.append(f"Estimated delivery: {order_data['estimated_delivery']}")

        if order_data.get("tracking_number"):
            details.append(f"Tracking: {order_data['tracking_number']}")

        if order_data.get("shipping_address"):
            details.append(f"Shipping to: {order_data['shipping_address']}")

        return " | ".join(details) if details else "No additional details available."

    async def update_order_status(self, order_number: str, status: str) -> APIResponse:
        """Update order status"""
        endpoint = f"/orders/{order_number}/status"
        data = {"status": status}

        return await self.circuit_breaker.call(
            self._make_request, "PUT", endpoint, data=data
        )

    async def health_check(self) -> ServiceStatus:
        """Check order service health"""
        try:
            response = await self._make_request("GET", "/health", use_cache=False)
            return ServiceStatus.HEALTHY if response.success else ServiceStatus.DEGRADED
        except:
            return ServiceStatus.UNAVAILABLE


class InventoryService(BaseService):
    """Inventory Management System integration"""

    async def check_availability(
        self, product_id: str, location: Optional[str] = None
    ) -> APIResponse:
        """Check product availability"""
        try:
            endpoint = f"/inventory/{product_id}"
            params = {}

            if location:
                params["location"] = location

            response = await self.circuit_breaker.call(
                self._make_request, "GET", endpoint, params
            )

            if response.success and response.data:
                inventory_data = response.data

                transformed_data = {
                    "inventory_info": {
                        "product_name": inventory_data.get("product_name", product_id),
                        "in_stock": inventory_data.get("available_quantity", 0) > 0,
                        "quantity": inventory_data.get("available_quantity", 0),
                        "restock_date": inventory_data.get("restock_date"),
                    }
                }

                return APIResponse(success=True, data=transformed_data)

            return APIResponse(
                success=True,
                data={
                    "inventory_info": {
                        "product_name": product_id,
                        "in_stock": False,
                        "quantity": 0,
                        "restock_date": "Unknown",
                    }
                },
            )

        except Exception as e:
            logger.error(f"Error checking inventory for {product_id}: {str(e)}")
            return APIResponse(success=False, error=str(e))

    async def reserve_inventory(self, product_id: str, quantity: int) -> APIResponse:
        """Reserve inventory for an order"""
        endpoint = f"/inventory/{product_id}/reserve"
        data = {"quantity": quantity}

        return await self.circuit_breaker.call(
            self._make_request, "POST", endpoint, data=data
        )

    async def health_check(self) -> ServiceStatus:
        """Check inventory service health"""
        try:
            response = await self._make_request("GET", "/health", use_cache=False)
            return ServiceStatus.HEALTHY if response.success else ServiceStatus.DEGRADED
        except:
            return ServiceStatus.UNAVAILABLE


class ProductService(BaseService):
    """Product Information System integration"""

    async def get_product_info(self, product_id: str) -> APIResponse:
        """Get detailed product information"""
        try:
            endpoint = f"/products/{product_id}"

            response = await self.circuit_breaker.call(
                self._make_request, "GET", endpoint
            )

            if response.success and response.data:
                product_data = response.data

                transformed_data = {
                    "product_info": {
                        "found": True,
                        "name": product_data.get("name", product_id),
                        "details": self._format_product_details(product_data),
                    }
                }

                return APIResponse(success=True, data=transformed_data)

            return APIResponse(
                success=True,
                data={"product_info": {"found": False}},
                error="Product not found",
            )

        except Exception as e:
            logger.error(f"Error getting product info for {product_id}: {str(e)}")
            return APIResponse(success=False, error=str(e))

    def _format_product_details(self, product_data: Dict) -> str:
        """Format product details for display"""
        details = []

        if product_data.get("description"):
            details.append(product_data["description"])

        if product_data.get("price"):
            details.append(f"Price: ${product_data['price']}")

        if product_data.get("specifications"):
            specs = product_data["specifications"]
            if isinstance(specs, dict):
                spec_text = ", ".join([f"{k}: {v}" for k, v in specs.items()])
                details.append(f"Specifications: {spec_text}")

        return " | ".join(details) if details else "No details available."

    async def search_products(self, query: str, limit: int = 10) -> APIResponse:
        """Search for products"""
        endpoint = "/products/search"
        params = {"query": query, "limit": limit}

        return await self.circuit_breaker.call(
            self._make_request, "GET", endpoint, params
        )

    async def health_check(self) -> ServiceStatus:
        """Check product service health"""
        try:
            response = await self._make_request("GET", "/health", use_cache=False)
            return ServiceStatus.HEALTHY if response.success else ServiceStatus.DEGRADED
        except:
            return ServiceStatus.UNAVAILABLE


class StoreService(BaseService):
    """Store Locator Service integration"""

    async def find_stores(self, location: str, radius: int = 25) -> APIResponse:
        """Find stores near a location"""
        try:
            endpoint = "/stores/search"
            params = {"location": location, "radius": radius}

            response = await self.circuit_breaker.call(
                self._make_request, "GET", endpoint, params
            )

            if response.success and response.data:
                stores_data = response.data.get("stores", [])

                transformed_data = {
                    "stores": [
                        {
                            "name": store.get("name", "Store"),
                            "address": store.get("address", "Address not available"),
                            "phone": store.get("phone"),
                            "hours": store.get("hours"),
                            "distance": store.get("distance"),
                        }
                        for store in stores_data
                    ]
                }

                return APIResponse(success=True, data=transformed_data)

            return APIResponse(
                success=True, data={"stores": []}, error="No stores found"
            )

        except Exception as e:
            logger.error(f"Error finding stores near {location}: {str(e)}")
            return APIResponse(success=False, error=str(e))

    async def get_store_details(self, store_id: str) -> APIResponse:
        """Get detailed store information"""
        endpoint = f"/stores/{store_id}"

        return await self.circuit_breaker.call(self._make_request, "GET", endpoint)

    async def health_check(self) -> ServiceStatus:
        """Check store service health"""
        try:
            response = await self._make_request("GET", "/health", use_cache=False)
            return ServiceStatus.HEALTHY if response.success else ServiceStatus.DEGRADED
        except:
            return ServiceStatus.UNAVAILABLE


class MockService(BaseService):
    """Mock service for development and testing"""

    def __init__(self):
        super().__init__("http://mock-service", None)
        self.mock_data = {
            "orders": {
                "AB12345678": {
                    "order_number": "AB12345678",
                    "status": "shipped",
                    "estimated_delivery": "Tomorrow",
                    "tracking_number": "TRK123456789",
                    "shipping_address": "123 Main St, Anytown, USA",
                }
            },
            "products": {
                "iphone13": {
                    "name": "iPhone 13",
                    "description": "Latest Apple smartphone with A15 Bionic chip",
                    "price": 799.99,
                    "specifications": {
                        "screen_size": "6.1 inches",
                        "storage": "128GB",
                        "color": "Blue",
                    },
                }
            },
            "inventory": {
                "iphone13": {
                    "product_name": "iPhone 13",
                    "available_quantity": 15,
                    "restock_date": "2024-01-15",
                }
            },
            "stores": [
                {
                    "name": "Downtown Store",
                    "address": "123 Main Street, Downtown",
                    "phone": "(555) 123-4567",
                    "hours": "Mon-Sat 9AM-9PM, Sun 10AM-6PM",
                    "distance": "0.5 miles",
                },
                {
                    "name": "Mall Location",
                    "address": "456 Shopping Center Dr",
                    "phone": "(555) 987-6543",
                    "hours": "Mon-Sat 10AM-10PM, Sun 11AM-7PM",
                    "distance": "2.3 miles",
                },
            ],
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        use_cache: bool = True,
    ) -> APIResponse:
        """Mock request implementation"""
        await asyncio.sleep(0.1)  # Simulate network delay

        if "/orders/" in endpoint:
            order_number = endpoint.split("/")[-1]
            if order_number in self.mock_data["orders"]:
                return APIResponse(
                    success=True, data=self.mock_data["orders"][order_number]
                )
            else:
                return APIResponse(
                    success=False, error="Order not found", status_code=404
                )

        elif "/products/" in endpoint:
            product_id = endpoint.split("/")[-1]
            if product_id in self.mock_data["products"]:
                return APIResponse(
                    success=True, data=self.mock_data["products"][product_id]
                )
            else:
                return APIResponse(
                    success=False, error="Product not found", status_code=404
                )

        elif "/inventory/" in endpoint:
            product_id = endpoint.split("/")[-1]
            if product_id in self.mock_data["inventory"]:
                return APIResponse(
                    success=True, data=self.mock_data["inventory"][product_id]
                )
            else:
                return APIResponse(success=True, data={"available_quantity": 0})

        elif "/stores/" in endpoint:
            return APIResponse(success=True, data={"stores": self.mock_data["stores"]})

        elif endpoint == "/health":
            return APIResponse(success=True, data={"status": "healthy"})

        return APIResponse(success=False, error="Endpoint not found", status_code=404)

    async def health_check(self) -> ServiceStatus:
        """Mock service is always healthy"""
        return ServiceStatus.HEALTHY


class BackendIntegrator:
    """
    Main backend integration coordinator

    This class manages all backend service integrations and provides
    a unified interface for the chatbot to interact with external systems.
    """

    def __init__(self, settings: Settings):
        """Initialize backend integrator with settings"""
        self.settings = settings
        self.services = {}
        self.use_mock_services = False

    async def initialize(self):
        """Initialize all backend services"""
        try:
            logger.info("Initializing backend integrator...")

            # Determine if we should use mock services
            if (
                self.settings.ENVIRONMENT == "development"
                or not self.settings.ORDER_API_BASE_URL
                or self.settings.ORDER_API_BASE_URL == "https://api.example.com/orders"
            ):
                self.use_mock_services = True
                logger.info("Using mock services for development")

            if self.use_mock_services:
                # Use mock services
                mock_service = MockService()
                self.services = {
                    "order": mock_service,
                    "inventory": mock_service,
                    "product": mock_service,
                    "store": mock_service,
                }
            else:
                # Use real services
                self.services = {
                    "order": OrderService(
                        self.settings.ORDER_API_BASE_URL, self.settings.ORDER_API_KEY
                    ),
                    "inventory": InventoryService(
                        self.settings.INVENTORY_API_BASE_URL,
                        self.settings.INVENTORY_API_KEY,
                    ),
                    "product": ProductService(
                        self.settings.PRODUCT_API_BASE_URL,
                        self.settings.PRODUCT_API_KEY,
                    ),
                    "store": StoreService(
                        self.settings.STORE_API_BASE_URL, self.settings.STORE_API_KEY
                    ),
                }

            logger.info("✅ Backend integrator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize backend integrator: {str(e)}")
            raise

    async def process_request(
        self,
        intent: str,
        entities: Dict[str, Any],
        context: Dict[str, Any],
        customer_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a request based on intent and entities"""

        try:
            if intent == "track_order":
                return await self._handle_order_tracking(entities, customer_id)

            elif intent == "inventory_check":
                return await self._handle_inventory_check(entities)

            elif intent == "product_info":
                return await self._handle_product_info(entities)

            elif intent == "store_locator":
                return await self._handle_store_locator(entities)

            elif intent == "pricing":
                return await self._handle_pricing(entities)

            else:
                return {"error": f"Unsupported intent: {intent}"}

        except Exception as e:
            logger.error(f"Error processing backend request: {str(e)}")
            return {"error": str(e)}

    async def _handle_order_tracking(
        self, entities: Dict, customer_id: Optional[str]
    ) -> Dict:
        """Handle order tracking requests"""
        order_numbers = entities.get("order_number", [])

        if not order_numbers:
            return {"error": "No order number provided"}

        order_number = order_numbers[0]
        response = await self.services["order"].get_order(order_number, customer_id)

        return response.data if response.success else {"error": response.error}

    async def _handle_inventory_check(self, entities: Dict) -> Dict:
        """Handle inventory check requests"""
        products = entities.get("products", []) or entities.get("product_mention", [])

        if not products:
            return {"error": "No product specified"}

        product_id = products[0].lower().replace(" ", "")
        response = await self.services["inventory"].check_availability(product_id)

        return response.data if response.success else {"error": response.error}

    async def _handle_product_info(self, entities: Dict) -> Dict:
        """Handle product information requests"""
        products = entities.get("products", []) or entities.get("product_mention", [])

        if not products:
            return {"error": "No product specified"}

        product_id = products[0].lower().replace(" ", "")
        response = await self.services["product"].get_product_info(product_id)

        return response.data if response.success else {"error": response.error}

    async def _handle_store_locator(self, entities: Dict) -> Dict:
        """Handle store locator requests"""
        locations = entities.get("locations", []) or entities.get("store_location", [])

        if not locations:
            # Default to nearby stores
            location = "current location"
        else:
            location = locations[0]

        response = await self.services["store"].find_stores(location)

        return response.data if response.success else {"error": response.error}

    async def _handle_pricing(self, entities: Dict) -> Dict:
        """Handle pricing requests"""
        products = entities.get("products", [])

        if not products:
            return {"error": "No product specified"}

        product_id = products[0].lower().replace(" ", "")
        response = await self.services["product"].get_product_info(product_id)

        if response.success and response.data:
            product_info = response.data.get("product_info", {})
            if "price" in str(product_info.get("details", "")):
                return {
                    "pricing_info": {
                        "product_name": product_info.get("name", product_id),
                        "price": "See product details",
                        "promotion": "Check our website for current promotions",
                    }
                }

        return {"error": "Pricing information not available"}

    async def get_health_status(self) -> Dict[str, ServiceStatus]:
        """Get health status of all services"""
        health_status = {}

        for service_name, service in self.services.items():
            try:
                status = await service.health_check()
                health_status[service_name] = status.value
            except Exception as e:
                logger.error(f"Health check failed for {service_name}: {str(e)}")
                health_status[service_name] = ServiceStatus.UNAVAILABLE.value

        return health_status

    async def cleanup(self):
        """Cleanup resources"""
        # Close any open connections, etc.
        pass


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    from config.settings import Settings

    async def test_backend_integrator():
        """Test the backend integrator"""
        settings = Settings()
        integrator = BackendIntegrator(settings)
        await integrator.initialize()

        print("Testing Backend Integrator")
        print("=" * 50)

        # Test order tracking
        result = await integrator.process_request(
            "track_order", {"order_number": ["AB12345678"]}, {}, "customer_123"
        )
        print(f"Order tracking result: {result}")

        # Test product info
        result = await integrator.process_request(
            "product_info", {"products": ["iPhone 13"]}, {}
        )
        print(f"Product info result: {result}")

        # Test inventory check
        result = await integrator.process_request(
            "inventory_check", {"products": ["iPhone 13"]}, {}
        )
        print(f"Inventory check result: {result}")

        # Test health status
        health = await integrator.get_health_status()
        print(f"Service health: {health}")

        await integrator.cleanup()

    # Run test
    asyncio.run(test_backend_integrator())
