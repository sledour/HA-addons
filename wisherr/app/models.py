from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=True)

    # On pointe vers les nouvelles classes
    quick_notes = relationship("QuickNote", back_populates="owner", cascade="all, delete-orphan")
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")

class QuickNote(Base):
    __tablename__ = "quick_notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="quick_notes")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    product_url = Column(String, nullable=True)
    source_type = Column(String) # 'search', 'link', 'manual', 'photo'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")