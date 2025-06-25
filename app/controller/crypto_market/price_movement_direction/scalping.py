from datetime import datetime, timedelta
import pandas as pd
from app.controller.crypto_market.price_movement_direction.indicators import calculate_rsi, calculate_macd, \
    calculate_ema
from app.model.db.queries.crypto_tickers import get_all_crypto_tickers_by_symbol_and_from_timestamp


async def scalping_analysis(symbol: str, session):
    votes = {
        "LONG": 0,
        "SHORT": 0,
        "HOLD": 0
    }

    explanation = "📊 Пояснення:\n\n"

    # Встановлюємо часові рамки (останні 6 годин)
    start_timestamp = int((datetime.now() - timedelta(hours=6)).timestamp() * 1000)
    rows = await get_all_crypto_tickers_by_symbol_and_from_timestamp(session, symbol, start_timestamp)

    df = pd.DataFrame(rows)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    latest = rows[0]
    previous = rows[1]
    close = df["close"]

    # RSI
    rsi = calculate_rsi(close, 7).iloc[-1]
    if rsi < 20:
        votes["LONG"] += 1
        explanation += f"✅ RSI ({rsi:.2f}) вказує на перепроданість — сигнал LONG\n"
    elif rsi > 80:
        votes["SHORT"] += 1
        explanation += f"⚠️ RSI ({rsi:.2f}) вказує на перекупленість — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ RSI ({rsi:.2f}) в нейтральній зоні — сигнал HOLD\n"

    # MACD
    macd_line, signal_line, _ = calculate_macd(close, 6, 13, 5)
    if macd_line.iloc[-1] > signal_line.iloc[-1]:
        votes["LONG"] += 1
        explanation += f"✅ MACD ({macd_line.iloc[-1]:.2f}) вище сигнальної ({signal_line.iloc[-1]:.2f}) — сигнал LONG\n"
    elif macd_line.iloc[-1] < signal_line.iloc[-1]:
        votes["SHORT"] += 1
        explanation += f"⚠️ MACD ({macd_line.iloc[-1]:.2f}) нижче сигнальної ({signal_line.iloc[-1]:.2f}) — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ MACD ≈ сигнальна лінія — сигнал HOLD\n"

    # EMA9
    ema9 = calculate_ema(close, 9)
    if close.iloc[-1] > ema9.iloc[-1]:
        votes["LONG"] += 1
        explanation += f"✅ Ціна ({close.iloc[-1]:.2f}) вище EMA9 ({ema9.iloc[-1]:.2f}) — сигнал LONG\n"
    elif close.iloc[-1] < ema9.iloc[-1]:
        votes["SHORT"] += 1
        explanation += f"⚠️ Ціна ({close.iloc[-1]:.2f}) нижче EMA9 ({ema9.iloc[-1]:.2f}) — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ Ціна ≈ EMA9 — сигнал HOLD\n"

    # EMA20
    ema20 = calculate_ema(close, 20)
    if close.iloc[-1] > ema20.iloc[-1]:
        votes["LONG"] += 1
        explanation += f"✅ Ціна ({close.iloc[-1]:.2f}) вище EMA20 ({ema20.iloc[-1]:.2f}) — сигнал LONG\n"
    elif close.iloc[-1] < ema20.iloc[-1]:
        votes["SHORT"] += 1
        explanation += f"⚠️ Ціна ({close.iloc[-1]:.2f}) нижче EMA20 ({ema20.iloc[-1]:.2f}) — сигнал SHORT\n"
    else:
        votes["HOLD"] += 1
        explanation += f"ℹ️ Ціна ≈ EMA20 — сигнал HOLD\n"

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

    # Ціна + обʼєм
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

    # Остаточне рішення
    if votes["LONG"] > votes["SHORT"]:
        result = f"{symbol.upper()} 🟢 LONG\n\n"
    elif votes["SHORT"] > votes["LONG"]:
        result = f"{symbol.upper()} 🔴 SHORT\n\n"
    else:
        result = f"{symbol.upper()} ⚪️ HOLD\n\n"

    result += explanation
    return result
