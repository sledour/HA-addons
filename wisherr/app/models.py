from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    wishlists = relationship("Wishlist", back_populates="owner")

class Wishlist(Base):
    __tablename__ = "wishlists"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="wishlists")
    items = relationship("Item", back_populates="wishlist")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    url = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    is_reserved = Column(Boolean, default=False)
    wishlist_id = Column(Integer, ForeignKey("wishlists.id"))
    
    wishlist = relationship("Wishlist", back_populates="items")