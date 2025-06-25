import asyncio
import aiohttp
import json
import websockets
import random
from sqlalchemy import insert
from app.model.db.database import async_engine
from app.model.db.models import crypto_tickers_data_table
from datetime import datetime, timedelta

BINANCE_API_URL = "https://api.binance.com/api/v3/klines"
BINANCE_FUTURES_OI_URL = "https://fapi.binance.com/fapi/v1/openInterest"

assets = [
    "BTCUSDT",
    "ETHUSDT"
]

oi_cache = {}


def fill_missing_ohlcv_data_randomly(rows: list[dict]) -> list[dict]:
    if not rows:
        return []

    numeric_fields = [
        "open", "high", "low", "close",
        "quote_asset_volume", "number_of_trades",
        "sum_open_interest", "sum_open_interest_value"
    ]

    min_max = {field: [float("inf"), float("-inf")] for field in numeric_fields}

    # Визначення діапазону для кожного поля
    for row in rows:
        for field in numeric_fields:
            value = row.get(field)
            if value is not None:
                min_max[field][0] = min(min_max[field][0], value)
                min_max[field][1] = max(min_max[field][1], value)

    # Заповнення пропусків
    filled_rows = []
    for row in rows:
        new_row = row.copy()
        for field in numeric_fields:
            if new_row.get(field) is None:
                min_val, max_val = min_max[field]
                if min_val < float("inf") and max_val > float("-inf"):
                    if isinstance(min_val, int) and isinstance(max_val, int):
                        new_row[field] = random.randint(int(min_val), int(max_val))
                    else:
                        new_row[field] = round(random.uniform(min_val, max_val), 8)
                else:
                    new_row[field] = 0.0  # якщо немає даних — заповнюємо нулем
        filled_rows.append(new_row)

    return filled_rows


async def fetch_open_interest(symbol: str) -> float:
    now = datetime.utcnow()
    if symbol in oi_cache:
        cached_value, timestamp = oi_cache[symbol]
        if now - timestamp < timedelta(seconds=30):
            return cached_value

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(BINANCE_FUTURES_OI_URL, params={"symbol": symbol}) as resp:
                data = await resp.json()
                oi = float(data["openInterest"])
                oi_cache[symbol] = (oi, now)
                return oi
        except Exception as e:
            print(f"OI fetch error: {e}")
            return 0.0


async def collect_historical_data(symbol: str, interval: str = "1m"):
    print(f"[{symbol}] Collecting historical data...")

    async with async_engine.begin() as conn:
        result = await conn.execute(
            crypto_tickers_data_table.select()
            .where(crypto_tickers_data_table.c.symbol == symbol)
            .order_by(crypto_tickers_data_table.c.timestamp.desc())
            .limit(1)
        )
        row = result.fetchone()
        start_time = row.timestamp + 1 if row else 0

    while True:
        url = f"{BINANCE_API_URL}?symbol={symbol}&interval={interval}&startTime={start_time}&limit=1000"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        if not data or "code" in data:
            break

        rows = []
        for d in data:
            try:
                oi = await fetch_open_interest(symbol)
            except Exception as e:
                print(f"OI error: {e}")
                oi = 0.0

            close_price = float(d[4])
            rows.append({
                "symbol": symbol,
                "timestamp": d[0],
                "open": float(d[1]),
                "high": float(d[2]),
                "low": float(d[3]),
                "close": close_price,
                "quote_asset_volume": float(d[7]),
                "number_of_trades": int(d[8]),
                "sum_open_interest": oi,
                "sum_open_interest_value": oi * close_price,
            })
        async with async_engine.begin() as conn:
            await conn.execute(insert(crypto_tickers_data_table), rows)
        print(f"[{symbol}] Inserted {len(rows)} rows")

        start_time = data[-1][0] + 60_000
        await asyncio.sleep(1)

    print(f"[{symbol}] Historical data collection complete.")


async def collect_live_data(symbol: str, interval: str):
    stream_name = f"{symbol.lower()}@kline_{interval}"
    url = f"wss://stream.binance.com:9443/ws/{stream_name}"

    async with websockets.connect(url) as websocket:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                k = data['k']
                if k['x']:
                    try:
                        oi = await fetch_open_interest(symbol)
                    except Exception as e:
                        print(f"Live OI error: {e}")
                        oi = 0.0

                    close_price = float(k['c'])
                    async with async_engine.begin() as conn:
                        await conn.execute(
                            insert(crypto_tickers_data_table).values(
                                symbol=symbol,
                                timestamp=k['t'],
                                open=float(k['o']),
                                high=float(k['h']),
                                low=float(k['l']),
                                close=close_price,
                                quote_asset_volume=float(k['q']),
                                number_of_trades=int(k['n']),
                                sum_open_interest=oi,
                                sum_open_interest_value=oi * close_price
                            )
                        )
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)


async def start_data_collection(symbol: str, interval: str):
    print("Collecting assets data...")
    await collect_historical_data(symbol, interval)
    await collect_live_data(symbol, interval)
