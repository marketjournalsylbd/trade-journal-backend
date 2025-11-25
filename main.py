from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models
import schemas
import crud
import csv_parser
from database import engine, SessionLocal   # ✅ Missing import fixed

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Single-user Trade Journal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------
# 📌 ADD NEW TRADE (MANUAL)
# ---------------------------
@app.post("/api/add-trade")
def add_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    try:
        created = crud.create_trade(db, trade)
        return {"status": "success", "trade_id": created.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------
# 📌 CSV UPLOAD
# ---------------------------
@app.post('/api/upload-csv')
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    trades = csv_parser.parse_csv_bytes(content)
    if not trades:
        raise HTTPException(status_code=400, detail="No valid trades parsed from CSV")
    created = []
    for t in trades:
        created.append(crud.create_trade(db, t))
    return {"imported": len(created)}


# ---------------------------
# 📌 LIST ALL TRADES
# ---------------------------
@app.get('/api/trades')
def list_trades(db: Session = Depends(get_db)):
    return crud.get_all_trades(db)


# ---------------------------
# 📌 SUMMARY
# ---------------------------
@app.get('/api/summary')
def get_summary(db: Session = Depends(get_db)):
    return crud.get_summary(db)
