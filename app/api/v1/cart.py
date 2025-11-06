from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.dependencies import get_current_user
from app.database import get_session
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
)
from app.schemas.product import ProductResponse

router = APIRouter()


def get_user_cart(user_id: int, session: Session) -> Cart:
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()

    if not cart:
        cart = Cart(user_id=user_id)

        session.add(cart)
        session.commit()
        session.refresh(cart)

    return cart


def build_cart_response(cart: Cart, session: Session) -> CartResponse:
    assert cart.id is not None

    cart_items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()

    items_response: list[CartItemResponse] = []
    total = Decimal(0)

    for item in cart_items:
        assert item.id is not None

        product = session.get(Product, item.product_id)
        if not product:
            continue

        subtotal = product.price * item.quantity
        total += subtotal

        items_response.append(
            CartItemResponse(
                id=item.id,
                product=ProductResponse(**product.model_dump()),
                quantity=item.quantity,
                subtotal=subtotal,
                added_at=item.added_at,
            )
        )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items_response,
        total=total,
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )


@router.get("/", response_model=CartResponse)
def get_my_cart(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    assert current_user.id is not None
    cart = get_user_cart(current_user.id, session)

    return build_cart_response(cart, session)


@router.post("/items", response_model=CartResponse)
def add_item_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    assert current_user.id is not None

    cart = get_user_cart(current_user.id, session)
    assert cart.id is not None

    product = session.get(Product, item_data.product_id)
    if not product:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Product not found")

    if product.stock_quantity < item_data.quantity:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Insufficient stock")

    existing_item = session.exec(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == item_data.product_id
        )
    ).first()

    if existing_item:
        new_quantity = existing_item.quantity + item_data.quantity
        if product.stock_quantity < new_quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, detail="Insufficient stock"
            )
        existing_item.quantity = new_quantity
        session.add(existing_item)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
        )
        session.add(new_item)

    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)

    session.commit()

    return build_cart_response(cart, session)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_cart_item(
    item_id: int,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    assert current_user.id is not None
    cart = get_user_cart(current_user.id, session)

    cart_item = session.get(CartItem, item_id)
    if not cart_item or cart_item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )

    product = session.get(Product, item_id)
    if product and product.stock_quantity < item_data.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock"
        )

    cart_item.quantity = item_data.quantity

    session.add(cart_item)

    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)

    session.commit()

    return build_cart_response(cart, session)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    assert current_user.id is not None
    cart = get_user_cart(current_user.id, session)

    cart_item = session.get(CartItem, item_id)
    if not cart_item or cart_item.cart_id != cart.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found"
        )

    session.delete(cart_item)

    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)

    session.commit()


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    assert current_user.id is not None
    cart = get_user_cart(current_user.id, session)

    cart_items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()

    for item in cart_items:
        session.delete(item)

    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)

    session.commit()
