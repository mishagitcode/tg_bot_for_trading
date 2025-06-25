from datetime import date, datetime, timedelta
import pandas as pd
from app.controller.crypto_market.price_movement_direction.indicators import calculate_macd, calculate_rsi, \
    calculate_ema
from app.model.db.queries.crypto_tickers import get_all_crypto_tickers_by_symbol_and_from_timestamp
from app.model.db.queries.fundamental_crypto_data import get_fear_and_greed_index_by_date


async def investing_analysis(symbol: str, session):
    votes = {
        "LONG": 0,
        "SHORT": 0,
        "HOLD": 0
    }

    explanation = "📊 Пояснення:\n\n"

    # Встановлюємо часові рамки (останні 180 днів)
    start_timestamp = int((datetime.now() - timedelta(days=180)).timestamp() * 1000)
    rows = await get_all_crypto_tickers_by_symbol_and_from_timestamp(session, symbol, start_timestamp)

    df = pd.DataFrame(rows)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    latest = rows[0]
    previous = rows[1]
    close = df["close"]

    # RSI
    rsi = calculate_rsi(close, 28).iloc[-1]
    if rsi < 30:
        votes["LONG"] += 1
        explanation += f"✅ RSI ({rsi:.2f}) вказує на перепроданість — сигнал LONG\n"
    elif rsi > 70:
        votes["SHORT"] += 1
        explanation += f"⚠️ RSI ({rsi:.2f}) вказує на перекупленість — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ RSI ({rsi:.2f}) в нейтральній зоні — сигнал HOLD\n"

    # MACD
    macd_line, signal_line, _ = calculate_macd(close, 19, 39, 12)
    if macd_line.iloc[-1] > signal_line.iloc[-1]:
        votes["LONG"] += 1
        explanation += f"✅ MACD ({macd_line.iloc[-1]:.2f}) вище сигнальної ({signal_line.iloc[-1]:.2f}) — сигнал LONG\n"
    elif macd_line.iloc[-1] < signal_line.iloc[-1]:
        votes["SHORT"] += 1
        explanation += f"⚠️ MACD ({macd_line.iloc[-1]:.2f}) нижче сигнальної ({signal_line.iloc[-1]:.2f}) — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ MACD ≈ сигнальна лінія — сигнал HOLD\n"

    # EMA50
    ema50 = calculate_ema(close, 50)
    if close.iloc[-1] > ema50.iloc[-1]:
        votes["LONG"] += 1
        explanation += f"✅ Ціна ({close.iloc[-1]:.2f}) вище EMA50 ({ema50.iloc[-1]:.2f}) — сигнал LONG\n"
    elif close.iloc[-1] < ema50.iloc[-1]:
        votes["SHORT"] += 1
        explanation += f"⚠️ Ціна ({close.iloc[-1]:.2f}) нижче EMA50 ({ema50.iloc[-1]:.2f}) — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ Ціна ≈ EMA50 — сигнал HOLD\n"

    # EMA100
    ema100 = calculate_ema(close, 100)
    if close.iloc[-1] > ema100.iloc[-1]:
        votes["LONG"] += 1
        explanation += f"✅ Ціна ({close.iloc[-1]:.2f}) вище EMA100 ({ema100.iloc[-1]:.2f}) — сигнал LONG\n"
    elif close.iloc[-1] < ema100.iloc[-1]:
        votes["SHORT"] += 1
        explanation += f"⚠️ Ціна ({close.iloc[-1]:.2f}) нижче EMA100 ({ema100.iloc[-1]:.2f}) — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ Ціна ≈ EMA100 — сигнал HOLD\n"

    # EMA200
    ema200 = calculate_ema(close, 200)
    if close.iloc[-1] > ema200.iloc[-1]:
        votes["LONG"] += 1
        explanation += f"✅ Ціна ({close.iloc[-1]:.2f}) вище EMA200 ({ema200.iloc[-1]:.2f}) — сигнал LONG\n"
    elif close.iloc[-1] < ema200.iloc[-1]:
        votes["SHORT"] += 1
        explanation += f"⚠️ Ціна ({close.iloc[-1]:.2f}) нижче EMA200 ({ema200.iloc[-1]:.2f}) — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ Ціна ≈ EMA200 — сигнал HOLD\n"

    # Ціна + об'єм
    if latest["close"] > previous["close"]:
        if latest["quote_asset_volume"] > previous["quote_asset_volume"]:
            votes["LONG"] += 1
            explanation += "✅ Ціна зросла разом із об'ємом — сигнал LONG\n"
        else:
            votes["SHORT"] += 1
            explanation += "⚠️ Ціна зросла, але об'єм впав — сигнал SHORT\n"

    # Ціна + відкритий інтерес
    if latest["close"] > previous["close"]:
        if latest["sum_open_interest"] > previous["sum_open_interest"]:
            votes["LONG"] += 1
            explanation += "✅ Ціна зросла разом із відкритим інтересом — сигнал LONG\n"
        else:
            votes["SHORT"] += 1
            explanation += "⚠️ Ціна зросла, але відкритий інтерес впав — сигнал SHORT\n"

    # Отримуємо сьогоднішній fear and greed index
    today = date.today()
    fear_greed_index = await get_fear_and_greed_index_by_date(session, today)

    if fear_greed_index is not None:
        if fear_greed_index > 75:
            votes["SHORT"] += 1
            explanation += f"⚠️ Fear & Greed Index = {fear_greed_index}, ринок жадібний — сигнал SHORT\n"
        elif fear_greed_index < 25:
            votes["LONG"] += 1
            explanation += f"✅ Fear & Greed Index = {fear_greed_index}, ринок боязкий — сигнал LONG\n"
        else:
            votes["HOLD"] += 1
            explanation += f"ℹ️ Fear & Greed Index = {fear_greed_index}, ринок нейтральний — сигнал HOLD\n"

    # Остаточне рішення
    if votes["LONG"] > votes["SHORT"]:
        result = f"{symbol.upper()} 🟢 LONG\n\n"
    elif votes["SHORT"] > votes["LONG"]:
        result = f"{symbol.upper()} 🔴 SHORT\n\n"
    else:
        result = f"{symbol.upper()} ⚪️ HOLD\n\n"

    result += explanation

    return result
