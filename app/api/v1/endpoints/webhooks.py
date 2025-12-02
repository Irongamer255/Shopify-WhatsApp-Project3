from fastapi import APIRouter, Request, HTTPException, Header, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Order, OrderStatus, User
from app.core.config import settings
import hmac
import hashlib
import base64
import json
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

async def verify_shopify_webhook(request: Request, x_shopify_hmac_sha256: str = Header(None)):
    if not x_shopify_hmac_sha256:
        raise HTTPException(status_code=401, detail="Missing HMAC header")
    
    body = await request.body()
    secret = settings.SHOPIFY_WEBHOOK_SECRET.encode('utf-8')
    digest = hmac.new(secret, body, hashlib.sha256).digest()
    computed_hmac = base64.b64encode(digest).decode('utf-8')
    
    if not hmac.compare_digest(computed_hmac, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")
    return True

@router.post("/{user_id}/orders/create")
async def handle_order_create(
    user_id: int,
    request: Request, 
    db: Session = Depends(get_db),
    verified: bool = Depends(verify_shopify_webhook)
):
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    payload = await request.json()
    logger.info(f"Received order create webhook for user {user_id}: {payload.get('id')}")
    
    # Extract relevant data
    shopify_order_id = str(payload.get("id"))
    order_number = str(payload.get("order_number"))
    customer = payload.get("customer", {})
    customer_phone = customer.get("phone") or payload.get("phone")
    customer_name = f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip()
    total_price = payload.get("total_price")
    currency = payload.get("currency")
    
    # Check if order already exists
    existing_order = db.query(Order).filter(Order.shopify_order_id == shopify_order_id).first()
    if existing_order:
        logger.info(f"Order {order_number} already exists. Skipping.")
        return {"status": "skipped", "reason": "duplicate"}
    
    # Create new order linked to user
    new_order = Order(
        user_id=user.id,
        shopify_order_id=shopify_order_id,
        order_number=order_number,
        customer_phone=customer_phone,
        customer_name=customer_name,
        total_price=total_price,
        currency=currency,
        financial_status=payload.get("financial_status"),
        fulfillment_status=payload.get("fulfillment_status"),
        status=OrderStatus.PENDING
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Trigger async task
    from app.worker.tasks import send_order_confirmation
    send_order_confirmation.apply_async(args=[new_order.id], countdown=10)
    
    # Broadcast to WebSocket clients (TODO: Filter by user)
    from app.services.websocket import manager
    await manager.broadcast({
        "type": "new_order",
        "data": {
            "order_number": new_order.order_number,
            "customer_name": new_order.customer_name,
            "total_price": new_order.total_price,
            "status": new_order.status.value,
            "delivery_slot": new_order.delivery_slot
        }
    })
    
    return {"status": "success", "order_id": new_order.id}
