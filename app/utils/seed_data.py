"""
Utility script to populate database with sample data
Run this after starting the app to add test restaurants and menu items
"""
from sqlmodel import Session
from app.core.database import engine
from app.core.security import get_password_hash
from app.models import User, Restaurant, MenuItem, DeliveryAgent


def seed_database():
    """Populate database with sample data"""
    
    with Session(engine) as session:
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@eatupnow.com",
            phone="+1234567890",
            hashed_password=get_password_hash("admin123"),
            address="123 Admin Street",
            role="admin"
        )
        session.add(admin)
        
        # Create regular user
        user = User(
            name="John Doe",
            email="john@example.com",
            phone="+1234567891",
            hashed_password=get_password_hash("password123"),
            address="456 User Avenue"
        )
        session.add(user)
        
        # Create delivery agent
        agent = DeliveryAgent(
            name="Mike Delivery",
            email="mike@delivery.com",
            phone="+1234567892",
            hashed_password=get_password_hash("delivery123"),
            vehicle_type="Bike",
            vehicle_number="DL-01-AB-1234"
        )
        session.add(agent)
        
        session.commit()
        
        # Create restaurants
        restaurants_data = [
            {
                "name": "The Golden Spice",
                "city": "New York",
                "address": "789 Food Street, NYC",
                "cuisine": "Indian",
                "rating": 4.5,
                "thumbnail": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400",
                "delivery_time": 35
            },
            {
                "name": "Pasta Paradise",
                "city": "New York",
                "address": "321 Italian Way, NYC",
                "cuisine": "Italian",
                "rating": 4.7,
                "thumbnail": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400",
                "delivery_time": 25
            },
            {
                "name": "Dragon Wok",
                "city": "Los Angeles",
                "address": "555 Asian Plaza, LA",
                "cuisine": "Chinese",
                "rating": 4.3,
                "thumbnail": "https://images.unsplash.com/photo-1525755662778-989d0524087e?w=400",
                "delivery_time": 40
            },
            {
                "name": "Burger Haven",
                "city": "Chicago",
                "address": "888 Burger Lane, Chicago",
                "cuisine": "American",
                "rating": 4.6,
                "thumbnail": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
                "delivery_time": 20
            },
            {
                "name": "Sushi Masters",
                "city": "San Francisco",
                "address": "222 Ocean Drive, SF",
                "cuisine": "Japanese",
                "rating": 4.8,
                "thumbnail": "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?w=400",
                "delivery_time": 30
            }
        ]
        
        restaurants = []
        for rest_data in restaurants_data:
            restaurant = Restaurant(**rest_data)
            session.add(restaurant)
            restaurants.append(restaurant)
        
        session.commit()
        
        # Create menu items for each restaurant
        menu_items_data = {
            "The Golden Spice": [
                {"name": "Butter Chicken", "description": "Creamy tomato curry with tender chicken", "price": 14.99, "category": "Main Course", "is_veg": False},
                {"name": "Paneer Tikka", "description": "Grilled cottage cheese with spices", "price": 12.99, "category": "Appetizer", "is_veg": True},
                {"name": "Vegetable Biryani", "description": "Aromatic rice with mixed vegetables", "price": 11.99, "category": "Main Course", "is_veg": True},
                {"name": "Mango Lassi", "description": "Sweet yogurt drink with mango", "price": 4.99, "category": "Beverage", "is_veg": True}
            ],
            "Pasta Paradise": [
                {"name": "Spaghetti Carbonara", "description": "Classic pasta with bacon and cream", "price": 16.99, "category": "Main Course", "is_veg": False},
                {"name": "Margherita Pizza", "description": "Fresh tomato, mozzarella, basil", "price": 13.99, "category": "Main Course", "is_veg": True},
                {"name": "Bruschetta", "description": "Toasted bread with tomatoes and basil", "price": 7.99, "category": "Appetizer", "is_veg": True},
                {"name": "Tiramisu", "description": "Classic Italian coffee dessert", "price": 6.99, "category": "Dessert", "is_veg": True}
            ],
            "Dragon Wok": [
                {"name": "Kung Pao Chicken", "description": "Spicy stir-fried chicken with peanuts", "price": 15.99, "category": "Main Course", "is_veg": False},
                {"name": "Vegetable Fried Rice", "description": "Wok-tossed rice with vegetables", "price": 10.99, "category": "Main Course", "is_veg": True},
                {"name": "Spring Rolls", "description": "Crispy vegetable rolls", "price": 6.99, "category": "Appetizer", "is_veg": True},
                {"name": "Hot and Sour Soup", "description": "Tangy spicy soup", "price": 5.99, "category": "Appetizer", "is_veg": True}
            ],
            "Burger Haven": [
                {"name": "Classic Cheeseburger", "description": "Beef patty with cheese and fixings", "price": 11.99, "category": "Main Course", "is_veg": False},
                {"name": "Veggie Burger", "description": "Plant-based patty with fresh toppings", "price": 10.99, "category": "Main Course", "is_veg": True},
                {"name": "Loaded Fries", "description": "Crispy fries with cheese and bacon", "price": 7.99, "category": "Appetizer", "is_veg": False},
                {"name": "Chocolate Shake", "description": "Thick creamy chocolate milkshake", "price": 5.99, "category": "Beverage", "is_veg": True}
            ],
            "Sushi Masters": [
                {"name": "California Roll", "description": "Crab, avocado, cucumber roll", "price": 13.99, "category": "Main Course", "is_veg": False},
                {"name": "Vegetable Roll", "description": "Fresh vegetable sushi roll", "price": 9.99, "category": "Main Course", "is_veg": True},
                {"name": "Miso Soup", "description": "Traditional Japanese soup", "price": 4.99, "category": "Appetizer", "is_veg": True},
                {"name": "Green Tea Ice Cream", "description": "Japanese green tea flavored ice cream", "price": 5.99, "category": "Dessert", "is_veg": True}
            ]
        }
        
        for restaurant in restaurants:
            if restaurant.name in menu_items_data:
                for item_data in menu_items_data[restaurant.name]:
                    menu_item = MenuItem(
                        restaurant_id=restaurant.id,
                        **item_data,
                        image=f"https://images.unsplash.com/photo-{1580000000000 + restaurant.id}?w=300"
                    )
                    session.add(menu_item)
        
        session.commit()
        
        print("✅ Database seeded successfully!")
        print("\n📝 Test Credentials:")
        print("Admin: admin@eatupnow.com / admin123")
        print("User: john@example.com / password123")
        print("Delivery: mike@delivery.com / delivery123")


if __name__ == "__main__":
    seed_database()
