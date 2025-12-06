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
from .core.database import create_db_and_tables
from .routers import auth, restaurants, menu, orders, reviews, delivery, upload, owner, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler
    Creates database tables on startup
    """
    print("🚀 Starting EatUpNow API...")
    
    # Only create database in non-serverless environments
    if os.getenv("VERCEL") != "1":
        create_db_and_tables()
        
        # Create uploads directory
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)
        print("📁 Uploads directory ready")
        print("✅ Database initialized")
    else:
        print("⚡ Running in Vercel serverless mode")
    
    yield
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
app.include_router(reviews.router)
app.include_router(delivery.router)
app.include_router(upload.router)
app.include_router(owner.router)
app.include_router(admin.router)

# Mount static files for uploaded images (only in non-serverless mode)
if os.getenv("VERCEL") != "1":
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
