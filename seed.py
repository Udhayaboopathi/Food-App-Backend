"""
Quick seed script for database
"""
from app.core.database import engine
from app.core.security import get_password_hash
from app.models import *
from sqlmodel import Session, SQLModel
from datetime import datetime

def seed_database():
    print("🌱 Seeding database...")
    
    with Session(engine) as session:
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@eatupnow.com",
            phone="1234567890",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            address="123 Admin St"
        )
        session.add(admin)
        
        # Create regular user
        user1 = User(
            name="John Doe",
            email="john@example.com",
            phone="9876543210",
            hashed_password=get_password_hash("password123"),
            role="user",
            address="456 User Ave"
        )
        session.add(user1)
        
        # Create owner user
        owner1 = User(
            name="Restaurant Owner",
            email="owner@restaurant.com",
            phone="5555555555",
            hashed_password=get_password_hash("owner123"),
            role="owner",
            address="789 Business Blvd"
        )
        session.add(owner1)
        
        session.commit()
        session.refresh(owner1)
        
        # Create restaurants
        restaurants = [
            Restaurant(
                name="Spice Paradise",
                city="New York",
                address="123 Curry Lane, Manhattan",
                cuisine="Indian",
                rating=4.5,
                thumbnail="https://images.unsplash.com/photo-1585937421612-70a008356fbe",
                delivery_time=35,
                owner_id=owner1.id
            ),
            Restaurant(
                name="Pasta Italia",
                city="Los Angeles",
                address="456 Pizza Street, Downtown",
                cuisine="Italian",
                rating=4.7,
                thumbnail="https://images.unsplash.com/photo-1555396273-367ea4eb4db5"
            ),
            Restaurant(
                name="Dragon Wok",
                city="Chicago",
                address="789 Noodle Road, Chinatown",
                cuisine="Chinese",
                rating=4.3,
                thumbnail="https://images.unsplash.com/photo-1526318896980-cf78c088247c"
            ),
            Restaurant(
                name="Burger Heaven",
                city="San Francisco",
                address="321 Grill Avenue, Bay Area",
                cuisine="American",
                rating=4.6,
                thumbnail="https://images.unsplash.com/photo-1568901346375-23c9450c58cd"
            ),
            Restaurant(
                name="Sushi Master",
                city="Seattle",
                address="654 Ocean Drive, Downtown",
                cuisine="Japanese",
                rating=4.8,
                thumbnail="https://images.unsplash.com/photo-1579584425555-c3ce17fd4351"
            )
        ]
        
        for restaurant in restaurants:
            session.add(restaurant)
        
        session.commit()
        
        # Link owner to first restaurant
        owner1.restaurant_id = restaurants[0].id
        session.add(owner1)
        session.commit()
        
        # Create menu items for each restaurant
        menu_items = [
            # Spice Paradise
            MenuItem(restaurant_id=restaurants[0].id, name="Butter Chicken", description="Creamy tomato curry", price=12.99, category="Main Course", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1603894584373-5ac82b2ae398"),
            MenuItem(restaurant_id=restaurants[0].id, name="Paneer Tikka", description="Grilled cottage cheese", price=10.99, category="Appetizer", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8"),
            MenuItem(restaurant_id=restaurants[0].id, name="Biryani", description="Aromatic rice dish", price=14.99, category="Main Course", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8"),
            MenuItem(restaurant_id=restaurants[0].id, name="Naan Bread", description="Soft flatbread", price=2.99, category="Sides", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1600173960614-5857128ff4ac"),
            
            # Pasta Italia
            MenuItem(restaurant_id=restaurants[1].id, name="Margherita Pizza", description="Classic tomato and mozzarella", price=11.99, category="Main Course", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1574071318508-1cdbab80d002"),
            MenuItem(restaurant_id=restaurants[1].id, name="Carbonara", description="Creamy pasta with bacon", price=13.99, category="Main Course", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1612874742237-6526221588e3"),
            MenuItem(restaurant_id=restaurants[1].id, name="Tiramisu", description="Classic Italian dessert", price=6.99, category="Dessert", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1571877227200-a0d98ea607e9"),
            MenuItem(restaurant_id=restaurants[1].id, name="Bruschetta", description="Toasted bread with tomatoes", price=7.99, category="Appetizer", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1572695157366-5e585ab2b69f"),
            
            # Dragon Wok
            MenuItem(restaurant_id=restaurants[2].id, name="Kung Pao Chicken", description="Spicy stir-fry", price=12.99, category="Main Course", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1525755662778-989d0524087e"),
            MenuItem(restaurant_id=restaurants[2].id, name="Spring Rolls", description="Crispy vegetable rolls", price=5.99, category="Appetizer", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1529928520614-7781a9f97cae"),
            MenuItem(restaurant_id=restaurants[2].id, name="Fried Rice", description="Wok-tossed rice", price=9.99, category="Main Course", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1603133872878-684f208fb84b"),
            MenuItem(restaurant_id=restaurants[2].id, name="Dumplings", description="Steamed pork dumplings", price=8.99, category="Appetizer", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1496116218417-1a781b1c416c"),
            
            # Burger Heaven
            MenuItem(restaurant_id=restaurants[3].id, name="Classic Burger", description="Beef patty with cheese", price=9.99, category="Main Course", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1568901346375-23c9450c58cd"),
            MenuItem(restaurant_id=restaurants[3].id, name="Veggie Burger", description="Plant-based patty", price=8.99, category="Main Course", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1520072959219-c595dc870360"),
            MenuItem(restaurant_id=restaurants[3].id, name="French Fries", description="Crispy golden fries", price=3.99, category="Sides", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1576107232684-1279f390859f"),
            MenuItem(restaurant_id=restaurants[3].id, name="Milkshake", description="Creamy vanilla shake", price=4.99, category="Beverages", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1572490122747-3968b75cc699"),
            
            # Sushi Master
            MenuItem(restaurant_id=restaurants[4].id, name="California Roll", description="Crab and avocado", price=11.99, category="Main Course", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1579584425555-c3ce17fd4351"),
            MenuItem(restaurant_id=restaurants[4].id, name="Salmon Sashimi", description="Fresh raw salmon", price=15.99, category="Main Course", is_veg=False, is_available=True, image="https://images.unsplash.com/photo-1599084993091-1cb5c0721cc6"),
            MenuItem(restaurant_id=restaurants[4].id, name="Edamame", description="Steamed soybeans", price=4.99, category="Appetizer", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1583876111861-ea4a4cec51ff"),
            MenuItem(restaurant_id=restaurants[4].id, name="Miso Soup", description="Traditional Japanese soup", price=3.99, category="Appetizer", is_veg=True, is_available=True, image="https://images.unsplash.com/photo-1559339352-11d035aa65de"),
        ]
        
        for item in menu_items:
            session.add(item)
        
        session.commit()
        
        print("✅ Database seeded successfully!")
        print(f"   - {len(restaurants)} restaurants")
        print(f"   - {len(menu_items)} menu items")
        print(f"   - 3 users (admin, user, owner)")
        print("\n📝 Test Credentials:")
        print("   Admin: admin@eatupnow.com / admin123")
        print("   User: john@example.com / password123")
        print("   Owner: owner@restaurant.com / owner123 (owns Spice Paradise)")

if __name__ == "__main__":
    seed_database()
