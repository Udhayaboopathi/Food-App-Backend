"""
Vercel serverless function entry point for FastAPI
"""
# Import the FastAPI app from the same directory (api/main.py)
from .main import app

# Vercel will use this 'app' variable as the ASGI application






