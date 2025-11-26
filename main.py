from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
import crud
import csv_parser
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Single-user Trade Journal API")

# ---------------------------
# CORS (Render + Vercel Compatible)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# DB Session
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# 📌 ADD NEW TRADE (MANUAL)
# =========================================================
@app.post("/api/add-trade")
def add_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    try:
        created = crud.create_trade(db, trade)
        return {"status": "success", "trade_id": created.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add trade: {e}")


# =========================================================
# 📌 CSV UPLOAD
# =========================================================
@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    trades = csv_parser.parse_csv_bytes(content)

    if not trades:
        raise HTTPException(status_code=400, detail="No valid trades parsed from CSV")

    created = []
    for t in trades:
        created.append(crud.create_trade(db, t))

    return {"imported": len(created)}


# =========================================================
# 📌 LIST ALL TRADES
# =========================================================
@app.get("/api/trades")
def list_trades(db: Session = Depends(get_db)):
    return crud.get_all_trades(db)


# =========================================================
# 📌 SUMMARY
# =========================================================
@app.get("/api/summary")
def get_summary(db: Session = Depends(get_db)):
    return crud.get_summary(db)


# =========================================================
# 📌 UPDATE TRADE
# =========================================================
@app.put("/api/trades/{trade_id}")
def update_trade(trade_id: int, payload: schemas.TradeCreate, db: Session = Depends(get_db)):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    # Update fields
    trade.symbol = payload.symbol
    trade.entry_time = payload.entry_time
    trade.exit_time = payload.exit_time
    trade.entry_price = payload.entry_price
    trade.exit_price = payload.exit_price
    trade.size = payload.size
    trade.direction = payload.direction        # ✅ added
    trade.fees = payload.fees
    trade.strategy = payload.strategy
    trade.notes = payload.notes

    # Direction-based PnL
    if payload.direction == "buy":
        pnl = (payload.exit_price - payload.entry_price) * payload.size
    else:  # sell
        pnl = (payload.entry_price - payload.exit_price) * payload.size

    pnl -= (payload.fees or 0.0)
    trade.pnl = pnl

    db.commit()
    db.refresh(trade)
    return {"status": "updated", "trade": trade}


# =========================================================
# 📌 DELETE TRADE
# =========================================================
@app.delete("/api/trades/{trade_id}")
def delete_trade(trade_id: int, db: Session = Depends(get_db)):
    trade = db.query(models.Trade).filter(models.Trade.id == trade_id).first()

    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    db.delete(trade)
    db.commit()
    return {"status": "deleted"}
