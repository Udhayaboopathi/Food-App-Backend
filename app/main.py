"""
EatUpNow FastAPI Main Application
Your hunger, handled instantly
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os

from .core.config import settings
from .core.database import connect_to_mongo, close_mongo_connection, is_db_connected
from .routers import auth, restaurants, menu, orders, upload, admin, owner


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler
    Connects to MongoDB on startup
    """
    print("🚀 Starting EatUpNow API...")
    
    # Connect to MongoDB (works for both local and Vercel)
    await connect_to_mongo()
    
    # Create uploads directory (only for local)
    if os.getenv("VERCEL") != "1":
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        print("📁 Uploads directory ready")
    else:
        print("⚡ Running in Vercel serverless mode")
    
    yield
    
    # Close MongoDB connection
    if os.getenv("VERCEL") != "1":
        await close_mongo_connection()
        print("👋 Shutting down EatUpNow API")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Fast food delivery API - Your hunger, handled instantly! 🍔",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(upload.router)
app.include_router(admin.router)
app.include_router(owner.router)

# Mount static files for uploaded images (only in non-serverless mode)
if os.getenv("VERCEL") != "1":
    # Mount each upload subfolder
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to EatUpNow API! 🍔",
        "slogan": "Your hunger, handled instantly",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "EatUpNow API",
        "version": settings.APP_VERSION
    }


@app.get("/db-check")
def database_check():
    """Database connection status endpoint"""
    db_connected = is_db_connected()
    return {
        "mongo_connected": db_connected,
        "status": "connected" if db_connected else "disconnected",
        "message": "MongoDB is operational" if db_connected else "MongoDB connection failed - check environment variables"
    }
