from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Config, Order
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ConfigUpdate(BaseModel):
    key: str
    value: str
    description: str = None

class OrderSchema(BaseModel):
    id: int
    order_number: str
    customer_name: str
    status: str
    total_price: str
    
    class Config:
        orm_mode = True

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    total_orders = db.query(Order).count()
    confirmed_orders = db.query(Order).filter(Order.status == OrderStatus.CONFIRMED).count()
    cancelled_orders = db.query(Order).filter(Order.status == OrderStatus.CANCELLED).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count()
    
    return {
        "total_orders": total_orders,
        "confirmed_rate": (confirmed_orders / total_orders * 100) if total_orders > 0 else 0,
        "cancellation_rate": (cancelled_orders / total_orders * 100) if total_orders > 0 else 0,
        "delivery_success_rate": (delivered_orders / total_orders * 100) if total_orders > 0 else 0
    }

from fastapi import BackgroundTasks

@router.post("/whatsapp/link")
def link_whatsapp_device(background_tasks: BackgroundTasks):
    """
    Triggers the Selenium browser to open for linking.
    Runs in background to not block the API.
    """
    from app.services.whatsapp_browser import SeleniumWhatsApp
    
    def run_linking():
        bot = SeleniumWhatsApp(headless=False)
        bot.link_device()
        
    background_tasks.add_task(run_linking)
    return {"status": "initiated", "message": "Browser opening... Please scan QR code."}

@router.get("/configs")
def get_configs(db: Session = Depends(get_db)):
    return db.query(Config).all()

@router.post("/configs")
def update_config(config: ConfigUpdate, db: Session = Depends(get_db)):
    db_config = db.query(Config).filter(Config.key == config.key).first()
    if db_config:
        db_config.value = config.value
        if config.description:
            db_config.description = config.description
    else:
        db_config = Config(key=config.key, value=config.value, description=config.description)
        db.add(db_config)
    db.commit()
    return {"status": "updated"}

@router.get("/orders", response_model=List[OrderSchema])
def get_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders
