from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime

def create_trade(db: Session, trade: schemas.TradeCreate):

    # --------------- 🔥 Direction-based PnL Calculation ---------------
    if trade.direction == "buy":
        pnl = (trade.exit_price - trade.entry_price) * trade.size
    else:  # sell trade
        pnl = (trade.entry_price - trade.exit_price) * trade.size

    # Fees adjust
    pnl -= (trade.fees or 0.0)

    # --------------- 🔥 Save to database ---------------
    db_trade = models.Trade(
        symbol=trade.symbol,
        entry_time=trade.entry_time or datetime.utcnow(),
        exit_time=trade.exit_time or datetime.utcnow(),
        entry_price=trade.entry_price,
        exit_price=trade.exit_price,
        size=trade.size,
        direction=trade.direction,     # ✅ NEW FIELD
        fees=trade.fees or 0.0,
        pnl=pnl,
        strategy=trade.strategy,
        notes=trade.notes,
    )

    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade


def get_all_trades(db: Session):
    return db.query(models.Trade).order_by(models.Trade.exit_time.asc()).all()


def get_summary(db: Session):
    trades = get_all_trades(db)

    total = sum(t.pnl for t in trades)
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl <= 0]

    win_rate = (len(wins) / len(trades) * 100) if trades else 0
    avg_win = (sum(t.pnl for t in wins) / len(wins)) if wins else 0
    avg_loss = (sum(t.pnl for t in losses) / len(losses)) if losses else 0

    return {
        "total_pnl": total,
        "num_trades": len(trades),
        "win_rate": win_rate,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
    }
