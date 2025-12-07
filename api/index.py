"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os

# Add parent directory to path so we can import from app/
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the FastAPI app from the root-level app/main.py
from app.main import app

# Vercel will use this 'app' variable as the ASGI application






