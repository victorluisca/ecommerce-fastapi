from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, desc, select  # type: ignore # noqa: F401

from app.api.dependencies import get_current_user, require_admin
from app.api.v1.cart import get_user_cart
from app.database import get_session
from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import (
    CheckoutResponse,
    OrderItemResponse,
    OrderResponse,
    OrderStatusUpdate,
)
from app.schemas.product import ProductResponse
from app.services.payment import create_checkout_session

router = APIRouter()


def build_order_response(order: Order, session: Session) -> OrderResponse:
    assert order.id is not None

    order_items = session.exec(
        select(OrderItem).where(OrderItem.order_id == order.id)
    ).all()

    items_response: list[OrderItemResponse] = []
    for item in order_items:
        assert item.id is not None

        product = session.get(Product, item.product_id)
        if not product:
            continue

        items_response.append(
            OrderItemResponse(
                id=item.id,
                product=ProductResponse(**product.model_dump()),
                quantity=item.quantity,
                price_at_purchase=item.price_at_purchase,
                subtotal=item.subtotal,
            )
        )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        items=items_response,
        total_price=order.total_price,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderResponse)
def create_order(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    assert current_user.id is not None

    cart = get_user_cart(current_user.id, session)
    cart_items = session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty"
        )

    total_price = Decimal(0)
    for item in cart_items:
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item.product_id} not found",
            )
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for {product.name}",
            )
        total_price += product.price * item.quantity

    order = Order(user_id=current_user.id, total_price=total_price)

    session.add(order)
    session.commit()
    session.refresh(order)

    assert order.id is not None

    for item in cart_items:
        product = session.get(Product, item.product_id)
        if not product:
            continue
        assert product.id is not None

        subtotal = product.price * item.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            price_at_purchase=product.price,
            subtotal=subtotal,
        )
        session.add(order_item)

        product.stock_quantity -= item.quantity
        session.add(product)

    for item in cart_items:
        session.delete(item)

    session.commit()

    return build_order_response(order, session)


@router.get("/", response_model=list[OrderResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    orders = session.exec(select(Order).where(Order.user_id == current_user.id)).all()
    return [build_order_response(order, session) for order in orders]


@router.get("/all", response_model=list[OrderResponse])
def get_all_orders(
    status: OrderStatus | None = Query(default=None),
    user_id: int | None = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)
    if user_id:
        query = query.where(Order.user_id == user_id)
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)  # type: ignore

    orders = session.exec(query).all()
    return [build_order_response(order, session) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    assert current_user.id is not None

    order = session.exec(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    return build_order_response(order, session)


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    admin: User = Depends(require_admin),
    session: Session = Depends(get_session),
):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    order.status = status_update.status

    session.add(order)
    session.commit()
    session.refresh(order)

    return build_order_response(order, session)


@router.post("/{order_id}/checkout", response_model=CheckoutResponse)
def create_order_checkout(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    order = session.exec(
        select(Order).where(Order.id == order_id, Order.user_id == current_user.id)
    ).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Order is already {order.status}",
        )

    try:
        checkout = create_checkout_session(
            order_id=order_id,
            amount=order.total_price,
        )

        order.stripe_checkout_session_id = checkout["id"]

        session.add(order)
        session.commit()

        return CheckoutResponse(session_id=checkout["id"], checkout_url=checkout["url"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout: {str(e)}",
        )
