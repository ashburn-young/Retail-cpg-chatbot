#!/usr/bin/env python3
"""
Simple test script to verify module imports work correctly.
This is used in CI to debug import issues.
"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Test basic module availability
try:
    import fastapi
    print("✅ FastAPI import successful")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    import pydantic
    print("✅ Pydantic import successful")
except ImportError as e:
    print(f"❌ Pydantic import failed: {e}")

# Test our module imports
print("\n--- Testing app module import ---")
try:
    # Set minimal environment variables for testing
    os.environ.setdefault('ENVIRONMENT', 'test')
    os.environ.setdefault('API_KEY', 'test-api-key')
    os.environ.setdefault('DEBUG', 'true')
    
    import app
    print("✅ App module import successful")
    print(f"App object type: {type(app.app) if hasattr(app, 'app') else 'No app attribute'}")
except ImportError as e:
    print(f"❌ App module import failed: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ App module initialization failed: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Testing individual module imports ---")
modules_to_test = [
    'config.settings',
    'modules.analytics', 
    'modules.context',
    'modules.integration',
    'modules.nlu',
    'modules.response'
]

for module_name in modules_to_test:
    try:
        exec(f"import {module_name}")
        print(f"✅ {module_name} import successful")
    except ImportError as e:
        print(f"❌ {module_name} import failed: {e}")
    except Exception as e:
        print(f"❌ {module_name} initialization failed: {e}")

print("\n--- Package installation check ---")
try:
    import pkg_resources
    try:
        pkg_resources.get_distribution('retail-cpg-chatbot')
        print("✅ retail-cpg-chatbot package is installed")
    except pkg_resources.DistributionNotFound:
        print("❌ retail-cpg-chatbot package not found")
except ImportError:
    print("❌ pkg_resources not available")
