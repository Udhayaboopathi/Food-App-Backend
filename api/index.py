"""
Vercel serverless function entry point
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

# Export the FastAPI app for Vercel
handler = app
