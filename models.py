# models.py

from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    entry_price = Column(Float)
    exit_price = Column(Float)
    size = Column(Float)
    direction = Column(String)       # <-- NEW FIELD
    fees = Column(Float, default=0.0)
    strategy = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    pnl = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
