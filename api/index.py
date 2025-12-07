"""
Vercel serverless function entry point for FastAPI
"""
import sys
from pathlib import Path

# Get the project root directory (parent of 'api' folder)
project_root = Path(__file__).parent.parent.resolve()

# Add project root to Python path if not already there
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import FastAPI app
try:
    from app.main import app
except ImportError as e:
    # Debugging: Print the error and sys.path
    print(f"Import Error: {e}")
    print(f"sys.path: {sys.path}")
    print(f"project_root: {project_root}")
    print(f"Files in project_root: {list(project_root.iterdir())}")
    raise

# Vercel requires the ASGI app to be named 'app' or exposed directly
# This is the entry point for Vercel's Python runtime


