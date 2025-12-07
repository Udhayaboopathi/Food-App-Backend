"""
Database configuration and session management
MongoDB/Beanie setup
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from .config import settings
import asyncio

# MongoDB client
mongodb_client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Initialize MongoDB connection"""
    global mongodb_client
    
    try:
        # Create MongoDB client with connection settings
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
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
        print("✅ MongoDB connected successfully")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("⚠️  Please check your MONGODB_URI in .env file")
        # Don't raise the exception to allow the app to start
        # The app will work without MongoDB (some endpoints will fail)


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("✅ MongoDB connection closed")


# Compatibility function for old code
def create_db_and_tables():
    """Compatibility function - MongoDB doesn't need table creation"""
    print("📊 Using MongoDB - no table creation needed")
    pass
