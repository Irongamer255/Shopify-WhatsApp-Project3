from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    api_key = Column(String(255), unique=True, index=True) # Internal API key
    
    # WhatsApp Config (Tier 3 support)
    whatsapp_api_token = Column(String(255), nullable=True)
    whatsapp_phone_number_id = Column(String(255), nullable=True)
    tier = Column(Integer, default=1) # 1=Shared, 2=Pool, 3=Own
    
    orders = relationship("Order", back_populates="merchant")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Link to User
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=True) # Keep for backward compat
    shopify_order_id = Column(String(255), unique=True, index=True)
    order_number = Column(String(255), index=True)
    customer_phone = Column(String(255))
    customer_name = Column(String(255))
    total_price = Column(String(255))
    currency = Column(String(50))
    financial_status = Column(String(50)) 
    fulfillment_status = Column(String(50))
    
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Delivery Details
    delivery_slot = Column(String(255), nullable=True)
    delivery_instructions = Column(Text, nullable=True)
    tracking_number = Column(String(255), nullable=True)
    tracking_url = Column(String(255), nullable=True)
    courier_name = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    merchant = relationship("Merchant", back_populates="orders")
    user = relationship("User", back_populates="orders")
    logs = relationship("MessageLog", back_populates="order")

class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    message_type = Column(String(50)) 
    status = Column(String(50)) 
    whatsapp_message_id = Column(String(255))
    content = Column(String(1000)) # Longer for content
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="logs")

class Config(Base):
    __tablename__ = "configs"
    
    key = Column(String(255), primary_key=True, index=True)
    value = Column(String(255))
    description = Column(String(255))
