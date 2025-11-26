from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class TradeBase(BaseModel):
    symbol: str
    entry_price: float
    exit_price: float
    size: float
    direction: Literal["buy", "sell"]         # ✅ New field added
    fees: Optional[float] = 0.0
    strategy: Optional[str] = None
    notes: Optional[str] = None
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None


class TradeCreate(TradeBase):
    pass


class Trade(TradeBase):
    id: int
    pnl: float
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
