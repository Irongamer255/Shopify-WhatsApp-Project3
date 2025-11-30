from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Order, OrderStatus, MessageLog
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """
    Verification endpoint for WhatsApp Webhook setup.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == "your_verify_token": # TODO: Move to config
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    return {"status": "ok"}

@router.post("/whatsapp")
async def handle_whatsapp_message(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    
    # Basic parsing of the payload
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        
        if not messages:
            return {"status": "no messages"}
            
        message = messages[0]
        from_number = message.get("from")
        msg_type = message.get("type")
        
        if msg_type == "interactive":
            interactive = message.get("interactive")
            inter_type = interactive.get("type")
            
            if inter_type == "button_reply":
                reply = interactive.get("button_reply")
                button_id = reply.get("id")
                # ... (existing button logic) ...
                action, order_id = button_id.split("_")
                order_id = int(order_id)
                
                order = db.query(Order).filter(Order.id == order_id).first()
                if not order: return {"status": "error"}

                if action == "confirm":
                    order.status = OrderStatus.CONFIRMED
                    logger.info(f"Order {order_id} confirmed.")
                    # Trigger Delivery Reminder after some time (e.g., 1 minute for demo)
                    from app.worker.tasks import send_delivery_reminder
                    send_delivery_reminder.apply_async(args=[order_id], countdown=60)
                    
                elif action == "cancel":
                    order.status = OrderStatus.CANCELLED
                    logger.info(f"Order {order_id} cancelled.")
                
                elif action == "address":
                    # In a real app, we'd set a state to expect text input next
                    pass
                
                db.commit()

            elif inter_type == "list_reply":
                reply = interactive.get("list_reply")
                list_id = reply.get("id") # e.g., slot_morning_123
                
                parts = list_id.split("_")
                # slot, morning, 123
                if parts[0] == "slot":
                    slot_time = parts[1]
                    order_id = int(parts[2])
                    
                    order = db.query(Order).filter(Order.id == order_id).first()
                    if order:
                        order.delivery_slot = slot_time
                        db.commit()
                        
                        # Ask for instructions
                        # For simplicity, we just acknowledge
                        # In real app, we might set state to wait for text
                        
                        # Trigger Tracking generation
                        from app.worker.tasks import generate_tracking_info
                        generate_tracking_info.apply_async(args=[order_id], countdown=30)

        elif msg_type == "text":
            # Handle text replies (e.g. for address change or instructions)
            # This requires session management which is complex for this snippet
            pass

            
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        
    return {"status": "received"}
