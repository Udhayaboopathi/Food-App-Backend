"""
Database configuration and session management
MongoDB/Beanie setup
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
import asyncio

# MongoDB client and initialization flag
mongodb_client: AsyncIOMotorClient = None
db_initialized: bool = False


async def connect_to_mongo():
    """Initialize MongoDB connection"""
    global mongodb_client, db_initialized
    
    try:
        print("🔌 Connecting to MongoDB...")
        
        # Create MongoDB client with connection settings
        # Use shorter timeout for Vercel serverless
        import os
        timeout_ms = 3000 if os.getenv("VERCEL") == "1" else 5000
        
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=timeout_ms,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=1  # Limit connections for serverless
        )
        
        # Test the connection
        await mongodb_client.admin.command('ping')
        
        # Import all models
        from ..models.user import User
        from ..models.restaurant import Restaurant
        from ..models.menu_item import MenuItem
        from ..models.order import Order
        from ..models.review import Review
        from ..models.delivery_agent import DeliveryAgent
        
        # Initialize beanie with all models
        await init_beanie(
            database=mongodb_client.eatupnow,
            document_models=[
                User,
                Restaurant,
                MenuItem,
                Order,
                Review,
                DeliveryAgent
            ]
        )
        
        db_initialized = True
        print("✅ MongoDB connected successfully")
        return True
        
    except Exception as e:
        db_initialized = False
        print(f"❌ MongoDB connection failed: {e}")
        print(f"⚠️  Error type: {type(e).__name__}")
        print("⚠️  Please check your MONGODB_URI in environment variables")
        # Don't raise the exception to allow the app to start
        # The app will work without MongoDB (some endpoints will fail)
        return False


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client, db_initialized
    if mongodb_client:
        mongodb_client.close()
        db_initialized = False
        print("✅ MongoDB connection closed")


def is_db_connected():
    """Check if database is connected and initialized"""
    global db_initialized
    return db_initialized


# Compatibility function for old code
def create_db_and_tables():
    """Compatibility function - MongoDB doesn't need table creation"""
    print("📊 Using MongoDB - no table creation needed")
    pass
