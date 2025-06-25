import os
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from aiogram.client.session import aiohttp
from dotenv import load_dotenv
from sqlalchemy import select, func, insert
from app.model.db.database import async_engine
from app.model.db.models import fundamental_data_table

load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")

INDICATORS = {
    "cpi": "CPIAUCSL",  # Consumer Price Index (1982–1984 = 100)
    "fed_rate": "FEDFUNDS",  # Effective Federal Funds Rate (%)
    "m2_global_money_supply": "M2SL",  # M2 Money Stock (Billions of $)
    "us_debt": "GFDEBTN",  # Total Public Debt (Millions of $)
    "vix_index": "VIXCLS",  # CBOE Volatility Index
    "treasury_yield_10y": "GS10",  # 10-Year Treasury Yield (%)

    # Економічна активність
    "real_gdp": "GDPC1",  # Real GDP (Billions of chained 2012 $)
    "unemployment_rate": "UNRATE",  # Unemployment Rate (%)
    "nonfarm_payrolls": "PAYEMS",  # Nonfarm Payrolls (Thousands)
    "industrial_production": "INDPRO",  # Industrial Production Index (2017=100)

    # Грошово-кредитна політика
    "m1_money_stock": "M1SL",  # M1 Money Stock (Billions of $)
    "fed_target_rate_upper": "DFEDTARU",  # Fed Target Rate Upper Bound (%)
    "total_consumer_credit": "TOTCI",  # Total Consumer Credit (Billions of $)
    "mortgage_rate_30y": "MORTGAGE30US",  # 30-Year Fixed Mortgage Rate (%)

    # Бюджет
    "federal_debt_to_gdp": "GFDGDPA188S",  # Federal Debt as % of GDP

    # Ринки
    "sp500_index": "SP500",  # S&P 500 Index
    "vxo_index": "VXOCLS",  # VXO Volatility Index (legacy VIX)
    "treasury_yield_2y": "GS2",  # 2-Year Treasury Yield (%)
    "treasury_yield_5y": "GS5",  # 5-Year Treasury Yield (%)
    "yield_curve_10y_2y": "T10Y2Y",  # Yield Curve: 10Y - 2Y Spread (%)

    # Інфляція
    "core_cpi": "CPILFESL",  # Core CPI (Excludes Food & Energy)
    "ppi_all_commodities": "PPIACO",  # Producer Price Index: All Commodities
    "import_price_index": "IR",  # Import Price Index (Index)

    # Торгівля
    "trade_balance": "BOPGSTB",  # Trade Balance (Millions of $)
    "exports": "EXPGS",  # Exports of Goods & Services (Billions of $)
    "imports": "IMPGS",  # Imports of Goods & Services (Billions of $)

    # Нерухомість
    "home_price_index": "CSUSHPINSA",  # S&P/Case-Shiller Home Price Index (Index)
    "new_home_sales": "HSN1F",  # New Home Sales (Thousands)
    "housing_starts": "HOUST",  # Housing Starts (Thousands)
}

BASE_URL = "https://api.stlouisfed.org/fred/series/observations"


def fill_missing_with_random(indicator_data: dict) -> dict:
    filled_data = {}

    for name, date_values in indicator_data.items():
        values = [v for v in date_values.values() if v is not None]
        if not values:
            continue  # якщо всі значення None — пропускаємо

        min_val = min(values)
        max_val = max(values)

        filled_data[name] = {}
        for date_str, value in date_values.items():
            if value is not None:
                filled_data[name][date_str] = value
            else:
                filled_data[name][date_str] = random.uniform(min_val, max_val)

    return filled_data


async def fetch_indicator(session, series_id, start_date, end_date):
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date.isoformat(),
        "observation_end": end_date.isoformat()
    }
    try:
        async with session.get(BASE_URL, params=params) as resp:
            data = await resp.json()
            if "observations" not in data:
                print(f"Error fetching {series_id}: {data}")
                return {}
            return {
                obs["date"]: float(obs["value"]) if obs["value"] not in ("", ".") else None
                for obs in data["observations"]
            }
    except Exception as e:
        print(f"⚠️ Exception while fetching {series_id}: {e}")
        return {}


async def collect_fundamental_data():
    today = date.today()

    async with async_engine.begin() as conn:
        result = await conn.execute(
            select(func.max(fundamental_data_table.c.date))
        )
        last_date = result.scalar()

    start_date = date(2017, 1, 1) if last_date is None else last_date + timedelta(days=1)
    if start_date > today:
        print("The data is already up to date. No collection is required.")
        return

    print(f"Collecting fundamental data from {start_date} to {today}...")

    async with aiohttp.ClientSession() as session:
        indicator_data = {}
        for name, series_id in INDICATORS.items():
            data = await fetch_indicator(session, series_id, start_date, today)
            if not data:
                print(f"Indicator ‘{name}’ is missing - no data.")
                continue
            indicator_data[name] = data

    if not indicator_data:
        print("No indicator was received. Skip saving.")
        return

    # Визначаємо спільний діапазон дат
    try:
        min_date_str = min(min(d.keys()) for d in indicator_data.values() if d)
        max_date_str = max(max(d.keys()) for d in indicator_data.values() if d)
    except ValueError:
        print("Date range cannot be defined. Skip saving.")
        return

    min_date = datetime.strptime(min_date_str, "%Y-%m-%d").date()
    max_date = datetime.strptime(max_date_str, "%Y-%m-%d").date()
    date_range = [min_date + timedelta(days=i) for i in range((max_date - min_date).days + 1)]

    last_values = defaultdict(lambda: None)
    rows = []

    for current_date in date_range:
        row = {"date": current_date}
        str_date = current_date.isoformat()

        for name in INDICATORS:
            value = indicator_data.get(name, {}).get(str_date)
            if value is not None:
                last_values[name] = value
            row[name] = last_values[name]
        rows.append(row)

    if not rows:
        print("There is no new fundamental data to save.")
        return

    async with async_engine.begin() as conn:
        await conn.execute(insert(fundamental_data_table), rows)

    print(f"Inserted {len(rows)} rows of fundamental data.")
