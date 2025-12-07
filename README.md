# EatUpNow API - MongoDB Backend

Fast food delivery API built with FastAPI and MongoDB Atlas.

## 🚀 Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Restaurant Management**: Browse restaurants, view menus, and place orders
- **Order Management**: Create, track, and manage orders
- **Admin Dashboard**: Manage users, restaurants, and orders
- **MongoDB Atlas**: Cloud-based NoSQL database
- **Async Operations**: Fully async codebase using Beanie ODM

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Environment configuration
│   │   ├── database.py        # MongoDB connection
│   │   └── security.py        # JWT & password hashing
│   ├── models/
│   │   ├── user.py           # User document model
│   │   ├── restaurant.py     # Restaurant document model
│   │   ├── menu_item.py      # Menu item document model
│   │   ├── order.py          # Order document model
│   │   ├── review.py         # Review document model
│   │   └── delivery_agent.py # Delivery agent document model
│   ├── routers/
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── restaurants.py    # Restaurant endpoints
│   │   ├── menu.py           # Menu management endpoints
│   │   ├── orders.py         # Order management endpoints
│   │   ├── admin.py          # Admin endpoints
│   │   └── upload.py         # File upload endpoints
│   ├── schemas/
│   │   ├── auth.py           # Auth request/response schemas
│   │   ├── restaurant.py     # Restaurant schemas
│   │   ├── menu_item.py      # Menu item schemas
│   │   └── order.py          # Order schemas
│   └── utils/
├── uploads/                   # Uploaded images directory
├── .env                       # Environment variables
├── main.py                    # Application entry point
└── requirements.txt           # Python dependencies

```

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create virtual environment**
```bash
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
Create a `.env` file:
```env
APP_NAME=EatUpNow API
APP_VERSION=2.0.0
DEBUG=True

# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

5. **Run the application**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Or for development with auto-reload:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Default Admin Credentials

After first run, the database will be seeded with:
- **Email**: admin@eatupnow.com
- **Password**: admin123

## 🎯 Key Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Restaurants
- `GET /restaurants` - List all restaurants
- `GET /restaurants/{id}` - Get restaurant details
- `POST /restaurants` - Create restaurant (Admin/Owner)
- `PUT /restaurants/{id}` - Update restaurant (Owner)
- `DELETE /restaurants/{id}` - Delete restaurant (Admin)

### Menu
- `GET /menu` - List menu items
- `GET /menu/restaurant/{restaurant_id}` - Get restaurant menu
- `POST /menu` - Add menu item (Owner)
- `PUT /menu/{id}` - Update menu item (Owner)
- `DELETE /menu/{id}` - Delete menu item (Owner)

### Orders
- `POST /orders` - Create new order
- `GET /orders` - Get user's orders
- `GET /orders/{id}` - Get order details
- `GET /orders/user/{user_id}` - Get orders by user (Admin)
- `PATCH /orders/{id}/status` - Update order status (Admin/Owner)
- `DELETE /orders/{id}` - Cancel order

### Admin
- `GET /admin/users` - List all users
- `GET /admin/restaurants` - List all restaurants
- `PUT /admin/users/{id}/role` - Update user role
- `DELETE /admin/users/{id}` - Delete user

## 🗄️ Database Schema

### Collections
- **users** - User accounts with roles (customer, owner, admin)
- **restaurants** - Restaurant information and ownership
- **menu_items** - Menu items linked to restaurants
- **orders** - Orders with embedded order items
- **reviews** - Restaurant reviews
- **delivery_agents** - Delivery agent information

## 🔄 Migration from SQLModel

This project has been migrated from SQLModel/SQLite to Beanie/MongoDB:
- ✅ Removed all SQLModel dependencies
- ✅ Converted all models to Beanie Documents
- ✅ Updated all routers to async MongoDB operations
- ✅ Implemented manual ObjectId serialization
- ✅ Cleaned up old SQLite files

## 🚨 Troubleshooting

**Port already in use:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /F /PID <process_id>
```

**MongoDB connection issues:**
- Verify MONGODB_URI in .env
- Check MongoDB Atlas network access settings
- Ensure IP address is whitelisted

**Import errors:**
- Delete all `__pycache__` directories
- Reinstall dependencies: `pip install -r requirements.txt`

## 📝 License

This project is for educational purposes.

## 👥 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

---

**Built with ❤️ using FastAPI & MongoDB**
