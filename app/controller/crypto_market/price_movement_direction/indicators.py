import pandas as pd


def calculate_ema(series: pd.Series, period: int = 20) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def calculate_macd(close_prices: pd.Series,
                   fast_ema_period: int = 12,
                   slow_ema_period: int = 26,
                   signal_ema_period: int = 9):
    fast_ema = calculate_ema(close_prices, fast_ema_period)
    slow_ema = calculate_ema(close_prices, slow_ema_period)
    macd_line = fast_ema - slow_ema
    signal_line = calculate_ema(macd_line, signal_ema_period)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_rsi(close_prices: pd.Series, period: int = 14):
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
