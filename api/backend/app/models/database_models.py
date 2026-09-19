import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, default="default_user", index=True)
    title = Column(String, default="New Biodiversity Diagnostic")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    profile = relationship("EnvironmentalProfileModel", back_populates="conversation", uselist=False, cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), index=True)
    role = Column(String)  # "user" or "assistant"
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")

class EnvironmentalProfileModel(Base):
    __tablename__ = "environmental_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), unique=True, index=True)
    
    # Soil
    soil_ph = Column(Float, nullable=True)
    organic_carbon = Column(Float, nullable=True)
    soil_moisture = Column(Float, nullable=True)
    
    # Climate
    rainfall = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    
    # Land
    land_use = Column(String, nullable=True)
    crop = Column(String, nullable=True)
    cropping_system = Column(String, nullable=True)
    
    # Biodiversity
    species_richness = Column(Integer, nullable=True)
    habitat_diversity = Column(String, nullable=True)
    
    # Human Impact
    pesticide_pressure = Column(String, nullable=True)
    pollution = Column(String, nullable=True)
    deforestation = Column(String, nullable=True)
    
    # Location
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    conversation = relationship("Conversation", back_populates="profile")

class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=True)
    organization = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    url = Column(String, nullable=False)
    source_type = Column(String, default="report")
    topic = Column(String, nullable=False)
    region = Column(String, default="Global")
    content = Column(Text, nullable=True)
    metrics = Column(String, nullable=True)  # Comma separated metrics
