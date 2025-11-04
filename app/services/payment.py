from decimal import Decimal
from typing import Any

import stripe

from app.config import settings

stripe.api_key = settings.stripe_secret_key


def create_checkout_session(
    order_id: int,
    amount: Decimal,
    currency: str = "usd",
    success_url: str = "http://localhost:8000/payment/success",
    cancel_url: str = "http://localhost:8000/payment/cancel",
) -> dict[str, Any]:
    amount_cents = int(amount * 100)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": currency,
                        "unit_amount": amount_cents,
                        "product_data": {
                            "name": f"Order #{order_id}",
                            "description": f"Payment for order #{order_id}",
                        },
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"order_id": str(order_id)},
        )

        return {"id": session.id, "url": session.url}
    except stripe.StripeError as e:
        raise Exception(f"Stripe error: {str(e)}")
