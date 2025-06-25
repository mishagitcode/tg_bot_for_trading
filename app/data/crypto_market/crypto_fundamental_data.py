import asyncio
from datetime import datetime, date
from sqlalchemy.dialects.mysql import insert
import aiohttp
from sqlalchemy import select
import random
from app.model.db.database import async_session_maker
from app.model.db.models import fundamental_crypto_data_table

FEAR_GREED_URL = "https://api.alternative.me/fng/?limit=0&format=json"
MARKET_METRICS_URL = "https://api.alternative.me/v2/ticker/?structure=array"


def fill_missing_crypto_data_randomly(rows: list[dict]) -> list[dict]:
    if not rows:
        return []

    keys = ["fear_greed_index", "btc_market_cap", "eth_market_cap", "total1", "total2", "total3"]
    min_max = {key: [float("inf"), float("-inf")] for key in keys}

    # 1. Визначаємо мінімальні та максимальні значення для кожного ключа
    for row in rows:
        for key in keys:
            value = row.get(key)
            if value is not None:
                min_max[key][0] = min(min_max[key][0], value)
                min_max[key][1] = max(min_max[key][1], value)

    # 2. Заповнюємо пропуски випадковими значеннями в межах [мін, макс]
    filled_rows = []
    for row in rows:
        filled_row = row.copy()
        for key in keys:
            if filled_row.get(key) is None:
                min_val, max_val = min_max[key]
                if min_val < float("inf") and max_val > float("-inf"):
                    filled_row[key] = random.uniform(min_val, max_val)
                else:
                    filled_row[key] = 0.0  # якщо всі значення були None — ставимо 0
        filled_rows.append(filled_row)

    return filled_rows


async def fetch_fear_greed_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(FEAR_GREED_URL) as response:
            data = await response.json()
            return data["data"]


async def fetch_market_metrics():
    async with aiohttp.ClientSession() as session:
        async with session.get(MARKET_METRICS_URL) as response:
            data = await response.json()
            return data["data"]


async def insert_fundamental_entry(session, record_date: date, fg_value: float, btc_cap: float = None,
                                   eth_cap: float = None, total1: float = None,
                                   total2: float = None, total3: float = None):
    stmt = insert(fundamental_crypto_data_table).values(
        date=record_date,
        fear_greed_index=fg_value,
        btc_market_cap=btc_cap,
        eth_market_cap=eth_cap,
        total1=total1,
        total2=total2,
        total3=total3
    ).on_duplicate_key_update(
        fear_greed_index=fg_value,
        btc_market_cap=btc_cap,
        eth_market_cap=eth_cap,
        total1=total1,
        total2=total2,
        total3=total3
    )
    await session.execute(stmt)
    await session.commit()


async def collect_historical_fundamental_crypto_data():
    fg_data = await fetch_fear_greed_data()
    async with async_session_maker() as session:
        for record in reversed(fg_data):
            timestamp = int(record["timestamp"])
            record_date = datetime.fromtimestamp(timestamp).date()
            value = float(record["value"])

            stmt = select(fundamental_crypto_data_table.c.id).where(
                fundamental_crypto_data_table.c.date == record_date
            )
            existing = await session.execute(stmt)
            if not existing.scalar():
                await insert_fundamental_entry(session, record_date, fg_value=value)


async def collect_live_fundamental_crypto_data():
    while True:
        print("[LIVE] Collecting fundamental crypto data")
        fg_data = await fetch_fear_greed_data()
        latest_fg = fg_data[0]
        timestamp = int(latest_fg["timestamp"])
        record_date = datetime.fromtimestamp(timestamp).date()
        fg_value = float(latest_fg["value"])

        market_data = await fetch_market_metrics()
        btc = next((x for x in market_data if x["name"] == "Bitcoin"), None)
        eth = next((x for x in market_data if x["name"] == "Ethereum"), None)

        btc_cap = btc.get("quotes", {}).get("USD", {}).get("market_cap") if btc else None
        eth_cap = eth.get("quotes", {}).get("USD", {}).get("market_cap") if eth else None

        total1 = sum(
            float(coin.get("quotes", {}).get("USD", {}).get("market_cap", 0))
            for coin in market_data
        )

        total2 = total1 - btc_cap if btc_cap else None
        total3 = total2 - eth_cap if eth_cap else None

        async with async_session_maker() as session:
            await insert_fundamental_entry(
                session, record_date, fg_value,
                btc_cap=btc_cap,
                eth_cap=eth_cap,
                total1=total1,
                total2=total2,
                total3=total3
            )

        await asyncio.sleep(86400)


async def collect_fundamental_crypto_data():
    await collect_historical_fundamental_crypto_data()
    asyncio.create_task(collect_live_fundamental_crypto_data())
