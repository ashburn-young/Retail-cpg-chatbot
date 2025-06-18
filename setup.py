"""
Setup configuration for Retail & CPG Customer Service Chatbot
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="retail-cpg-chatbot",
    version="1.0.0",
    author="Retail CPG Team",
    description="AI-powered customer service chatbot for retail and CPG companies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests*"]),
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.24.0",
        "aiohttp>=3.10.11",
        "pydantic[email]>=2.5.0",
        "pydantic-settings>=2.0.0",
        "spacy>=3.7.0",
        "jsonlines>=4.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "httpx>=0.25.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "bandit",
            "safety",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
