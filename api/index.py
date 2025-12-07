"""
Vercel serverless function entry point for FastAPI
"""
import sys
import os

# Add the api directory to Python path
# This allows us to import from api.app.main
api_dir = os.path.dirname(os.path.abspath(__file__))
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

# Debug: List what files exist
try:
    import json
    files_in_api = os.listdir(api_dir)
    app_exists = os.path.exists(os.path.join(api_dir, 'app'))
    
    debug_info = {
        "api_dir": api_dir,
        "files_in_api": files_in_api,
        "app_folder_exists": app_exists,
        "sys_path": sys.path[:5]
    }
    
    if app_exists:
        app_dir = os.path.join(api_dir, 'app')
        debug_info["files_in_app"] = os.listdir(app_dir)
except Exception as e:
    debug_info = {"error": str(e)}

# Try to import the app
try:
    from app.main import app
except ImportError as e:
    # If import fails, create a minimal FastAPI app that shows debug info
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="Debug Info")
    
    @app.get("/")
    def debug():
        return JSONResponse({
            "error": f"Failed to import app.main: {str(e)}",
            "debug": debug_info
        })
    
    @app.get("/health")
    def health():
        return {"status": "debug_mode", "error": str(e)}

# Vercel will use this 'app' variable as the ASGI application






