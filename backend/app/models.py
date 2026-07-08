from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Date
import enum

from app.database import Base


class InteractionType(str, enum.Enum):
    CALL = "Call"
    EMAIL = "Email"
    MEETING = "Meeting"
    OTHER = "Other"


class Sentiment(str, enum.Enum):
    POSITIVE = "Positive"
    NEUTRAL = "Neutral"
    NEGATIVE = "Negative"


class HCPInteraction(Base):
    __tablename__ = "hcp_interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String(255), nullable=False, default="")
    interaction_type = Column(String(50), nullable=False, default="")
    interaction_date = Column(Date, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    sentiment = Column(String(50), nullable=True, default="")
    specialty = Column(String(255), nullable=True, default="")
    region = Column(String(255), nullable=True, default="")
    products_discussed = Column(Text, nullable=True, default="")
    key_discussion_points = Column(Text, nullable=True, default="")
    action_items = Column(Text, nullable=True, default="")
    follow_up_date = Column(Date, nullable=True)
    additional_notes = Column(Text, nullable=True, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
