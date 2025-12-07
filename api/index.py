"""
Vercel serverless function entry point for FastAPI
This file re-exports the FastAPI app from app.main
"""

# For Vercel, we need to make the app module accessible
# The trick is that Vercel deploys everything in the project root
# So we import directly from app.main
from app.main import app

# Vercel's Python runtime expects the ASGI application to be named 'app'
# or accessible as a module-level variable



