"""
Vercel serverless function entry point for FastAPI
"""
# Import the FastAPI app from api/app/main.py
from app.main import app

# Vercel will use this 'app' variable as the ASGI application






