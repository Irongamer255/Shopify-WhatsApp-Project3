from app.worker.celery_app import celery_app
from app.services.whatsapp import whatsapp_service
from app.db.database import SessionLocal
from app.db.models import Order, OrderStatus, MessageLog
from app.core.config import settings
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Helper to run async code in sync Celery task
def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

@celery_app.task(bind=True)
def send_order_confirmation(self, order_id: int):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found.")
            return "Order not found"

        if order.status != OrderStatus.PENDING:
            logger.info(f"Order {order_id} is not pending (Status: {order.status}). Skipping confirmation.")
            return "Skipped"

        # Check Provider
        if settings.WHATSAPP_PROVIDER == "selenium":
            logger.info(f"Using Selenium Provider for Order {order.order_number}")
            try:
                from app.services.whatsapp_browser import SeleniumWhatsApp
                # Use user_id from order
                bot = SeleniumWhatsApp(user_id=order.user_id, headless=True) 
                bot.start()
                
                message = f"Hello {order.customer_name}, your order {order.order_number}} of {order.currency} {order.total_price} is confirmed!"
                bot.send_message(order.customer_phone, message)
                bot.close()
                
                # Log success
                log = MessageLog(
                    order_id=order.id,
                    message_type="selenium_text",
                    status="sent",
                    content=message
                )
                db.add(log)
                db.commit()
                
                # Update Order Status
                order.status = OrderStatus.CONFIRMED
                db.commit()
                
                # Broadcast status update via WebSocket
                from app.services.websocket import manager
                asyncio.run(manager.broadcast({
                    "type": "status_update",
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "status": order.status.value
                }))
                
                return "Message Sent (Selenium)"
                
            except Exception as e:
                logger.error(f"Selenium Error: {e}")
                # Log failure
                log = MessageLog(
                    order_id=order.id,
                    message_type="selenium_text",
                    status="failed",
                    content=str(e)
                )
                db.add(log)
                db.commit()
                return f"Selenium Failed: {e}"
        
        else:
            # OFFICIAL API (Existing Logic)
            logger.info(f"Using Official API for Order {order.order_number}")
            
            # Construct message
            # Using interactive buttons for Confirm / Change Address / Cancel
            buttons = [
                {"type": "reply", "reply": {"id": f"confirm_{order_id}", "title": "Confirm ✅"}},
                {"type": "reply", "reply": {"id": f"address_{order_id}", "title": "Change Addr 📍"}},
                {"type": "reply", "reply": {"id": f"cancel_{order_id}", "title": "Cancel ❌"}}
            ]
            
            body_text = f"Hello {order.customer_name}, thank you for your order #{order.order_number} of {order.currency} {order.total_price}. Please confirm your order details."

            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response = loop.run_until_complete(whatsapp_service.send_interactive_message(
                    to_phone=order.customer_phone,
                    body_text=body_text,
                    buttons=buttons
                ))
                loop.close()
                
                # Log the message
                log = MessageLog(
                    order_id=order.id,
                    message_type="confirmation",
                    status="sent",
                    whatsapp_message_id=response.get("messages", [{}])[0].get("id"),
                    content=body_text
                )
                db.add(log)
                db.commit()
                
                #Update Order Status
                order.status = OrderStatus.CONFIRMED
                db.commit()
                
                # Broadcast status update via WebSocket
                from app.services.websocket import manager
                asyncio.run(manager.broadcast({
                    "type": "status_update",
                    "order_id": order.id,
                    "order_number": order.order_number,
                    "status": order.status.value
                }))
                
                # Schedule follow-up check (e.g., 24 hours later)
                check_order_response.apply_async(args=[order_id], countdown=86400)
                
                return "Message Sent (Official)"
                
            except Exception as e:
                logger.error(f"Failed to send WhatsApp message: {e}")
                return f"Failed: {e}"

    finally:
        db.close()

from app.services.shopify import shopify_service

@celery_app.task(bind=True)
def check_order_response(self, order_id: int):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.status != OrderStatus.PENDING:
            return
            
        # Send follow-up reminder
        body_text = f"Hi {order.customer_name}, we are still waiting for your confirmation for order #{order.order_number}. Please confirm to avoid cancellation."
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(whatsapp_service.send_interactive_message(
                to_phone=order.customer_phone,
                body_text=body_text,
                buttons=[{"type": "reply", "reply": {"id": f"confirm_{order_id}", "title": "Confirm ✅"}}]
            ))
            loop.close()
            
            # Schedule auto-cancel
            auto_cancel_order.apply_async(args=[order_id], countdown=86400) # 24 hours later
            
        except Exception as e:
            logger.error(f"Failed to send follow-up: {e}")

    finally:
        db.close()

@celery_app.task(bind=True)
def auto_cancel_order(self, order_id: int):
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order or order.status != OrderStatus.PENDING:
            return
            
        # Cancel locally
        order.status = OrderStatus.CANCELLED
        db.commit()
        
        # Cancel on Shopify
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(shopify_service.cancel_order(order.shopify_order_id))
        
        # Notify user
        loop.run_until_complete(whatsapp_service.send_template_message(
            to_phone=order.customer_phone,
            template_name="order_cancelled_notification"
        ))
        loop.close()
        
    finally:
        db.close()
