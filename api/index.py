"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os

# Add the api directory to Python path
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

# Import the FastAPI app from api/app/main.py
from app.main import app

# Vercel will use this 'app' variable as the ASGI application






