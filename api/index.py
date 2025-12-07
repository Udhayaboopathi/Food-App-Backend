"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os
from importlib import import_module

# Get the directory containing this file
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import main module dynamically
main_module = import_module('main')
app = main_module.app

# Vercel will use this 'app' variable as the ASGI application






