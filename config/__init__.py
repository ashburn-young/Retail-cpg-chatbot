"""
Configuration Package
====================

This package contains configuration settings and environment management
for the Retail & CPG Customer Service Chatbot.
"""

from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
