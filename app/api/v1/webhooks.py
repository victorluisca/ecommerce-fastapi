import json
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models.order import Order, OrderStatus

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_session),
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        if settings.stripe_webhook_secret:
            event = stripe.Webhook.construct_event(  # type: ignore
                payload, sig_header, settings.stripe_webhook_secret
            )
        else:
            event = json.loads(payload)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload"
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
        )

    if event["type"] == "checkout.session.completed":
        session_data = event["data"]["object"]

        order_id = session_data["metadata"].get("order_id")
        if not order_id:
            return {"status": "error", "message": "No order_id in metadata"}

        order = db.exec(select(Order).where(Order.id == int(order_id))).first()

        if order:
            order.status = OrderStatus.PAID
            order.updated_at = datetime.now(timezone.utc)

            db.add(order)
            db.commit()

    return {"status": "success"}
