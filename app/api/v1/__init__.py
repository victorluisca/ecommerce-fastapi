from fastapi import APIRouter

from app.api.v1 import auth, cart, orders, products, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(cart.router, prefix="/cart", tags=["Shopping Cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
