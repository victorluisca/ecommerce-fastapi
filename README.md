# E-Commerce API

A RESTful API for an e-commerce platform built with FastAPI and SQLModel. This is a project idea from [roadmap.sh](https://roadmap.sh/projects/ecommerce-api)

## Features

- [x] User authentication with JWT
- [x] Role-based access control (customer/admin)
- [x] Product management
- [x] Shopping cart
- [x] Order processing with stock management
- [ ] Payment gateway integration
- [ ] Tests

## Tech Stack

- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

- Add dependency: `uv add package-name`
- Add dev dependency: `uv add --dev package-name`
- Run commands: `uv run <command>`
- Sync dependencies: `uv sync`

## Setup

1. Clone the repository
2. Install dependencies: `uv sync`
3. Copy `.env.example` to `.env` and configure
4. Create admin user: `uv run -m app.seed`
5. Run: `fastapi dev`

## Environment Variables

```
DATABASE_URL=sqlite:///./ecommerce.db
JWT_SECRET_KEY=your-secret-eky
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=AdminPassword123!
```

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints Overview

### Authentication

- **POST** `/api/v1/auth/register` - Register new user
- **POST** `/api/v1/auth/login` - Login and get JWT token

### Users

- **GET** `/api/v1/users/me` - Get profile
- **PATCH** `/api/v1/users/me` - Update profile
- **PUT** `/api/v1/users/me/password` - Change password

### Products

- **GET** `/api/v1/products` - List products
- **GET** `/api/v1/products/{id}` - Get product
- **POST** `/api/v1/products` - Create product (admin)
- **PATCH** `/api/v1/products/{id}` - Update product (admin)
- **DELETE** `/api/v1/products/{id}` - Delete product (admin)

### Shopping Cart

- **GET** `/api/v1/cart` - View cart
- **POST** `/api/v1/cart/items` - Add item
- **PATCH** `/api/v1/cart/items/{id}` - Update quantity
- **DELETE** `/api/v1/cart/items/{id}` - Remove item
- **DELETE** `/api/v1/cart` - Clear cart

### Orders

- **POST** `/api/v1/orders` - Create order from cart
- **GET** `/api/v1/orders` - List my orders
- **GET** `/api/v1/orders/{id}` - Get order detail
- **GET** `/api/v1/orders/all` - List all orders (admin)
- **PATCH** `/api/v1/orders/{id}` - Update order status (admin)

## Default Admin Account

Email: `admin@example.com`
<br>
Password: `AdminPassword123!`
