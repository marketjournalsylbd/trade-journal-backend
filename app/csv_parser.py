import pandas as pd
from typing import List
from .schemas import TradeCreate
from datetime import datetime

# A flexible CSV parser that attempts to map common column names to our schema.
COLUMN_MAP = {
    'symbol': ['symbol', 'ticker', 'instrument'],
    'entry_time': ['entry_time', 'open_time', 'entry_date', 'time_in'],
    'exit_time': ['exit_time', 'close_time', 'exit_date', 'time_out'],
    'entry_price': ['entry_price', 'open_price', 'buy_price', 'price_in'],
    'exit_price': ['exit_price', 'close_price', 'sell_price', 'price_out'],
    'size': ['size', 'quantity', 'qty', 'volume'],
    'fees': ['fees', 'commission'],
    'strategy': ['strategy', 'tag'],
    'notes': ['notes', 'comment']
}

def _find_col(df_cols, candidates):
    for c in candidates:
        if c in df_cols:
            return c
    # case-insensitive search
    lower = {x.lower(): x for x in df_cols}
    for c in candidates:
        if c.lower() in lower:
            return lower[c.lower()]
    return None

def parse_csv_bytes(content: bytes) -> List[TradeCreate]:
    df = pd.read_csv(pd.io.common.BytesIO(content))
    cols = df.columns.tolist()
    mapped = {}
    for key, candidates in COLUMN_MAP.items():
        col = _find_col(cols, candidates)
        if col:
            mapped[key] = col
    trades = []
    for _, row in df.iterrows():
        try:
            entry_time = pd.to_datetime(row[mapped.get('entry_time')]) if mapped.get('entry_time') else None
            exit_time = pd.to_datetime(row[mapped.get('exit_time')]) if mapped.get('exit_time') else None
            entry_price = float(row[mapped.get('entry_price')])
            exit_price = float(row[mapped.get('exit_price')])
            size = float(row[mapped.get('size')]) if mapped.get('size') else 1.0
            fees = float(row[mapped.get('fees')]) if mapped.get('fees') else 0.0
            symbol = str(row[mapped.get('symbol')]) if mapped.get('symbol') else 'UNKNOWN'
            strategy = str(row[mapped.get('strategy')]) if mapped.get('strategy') else None
            notes = str(row[mapped.get('notes')]) if mapped.get('notes') else None
            trade = TradeCreate(
                symbol=symbol,
                entry_time=entry_time.to_pydatetime() if entry_time is not None else None,
                exit_time=exit_time.to_pydatetime() if exit_time is not None else None,
                entry_price=entry_price,
                exit_price=exit_price,
                size=size,
                fees=fees,
                strategy=strategy,
                notes=notes,
            )
            trades.append(trade)
        except Exception as e:
            # skip row on error — we could collect errors and return them
            continue
    return trades
