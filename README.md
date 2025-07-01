# 📈 Trader's Recommender System Bot

## 🧠 Overview

This project is a **hybrid intelligent recommender system** for cryptocurrency traders. The system is implemented as a **Telegram bot** that helps users make data-driven trading decisions in real time based on:

- Expert rule-based systems (RSI, MACD, EMA, etc.)
- Deep learning models (LSTM, GRU, MLP)
- Live and historical market + macroeconomic data

> 🎯 **Goal:** Support traders in determining price direction and entry/exit points based on real-time analysis.

## 🧱 System Architecture

### 1. User Interface
- **Telegram Bot** (built with `aiogram`)
  - Receives user input
  - Allows selection of:
    - Analysis mode: _Price Direction_ or _Entry/Exit Point_
    - Trading style: _Scalping_, _Intraday_, _Swing_, _Investing_
    - Asset (e.g. BTC/USDT)

### 2. Data Flow

**Step 1: Data Collection Service**
- Fetches **historical and real-time** data from:
  - Binance API (candlestick, volume, open interest — every 1 min)
  - Alternative.me API (Fear & Greed Index, dominance, etc. — daily)
  - FRED API (macro indicators — daily)
- Fills missing data using:
  - Random sampling (short-term gaps)
  - Value propagation (for stable indicators like interest rates)

**Step 2: Database (MySQL)**
- Tables:
  - `crypto_tickers_data`: minute-level market data
  - `fundamental_crypto_data`: daily crypto indicators
  - `fundamental_data`: daily macroeconomic indicators
- Managed via **SQLAlchemy (async)**

### 3. Core Logic

#### A. Expert System
- Rule-based engine using technical indicators:
  - RSI, MACD, EMA, volume
- Voting mechanism per indicator
- Output: `BUY`, `SELL`, or `HOLD` signal

#### B. Neural Networks
- Models: `MLP`, `LSTM`, `GRU`
- Input: last 1000 close prices (normalized)
- Windowing: 50-time steps per sequence
- Evaluation metrics:
  - MAE, RMSE, R², MAPE
- Best model selected per run
- Output: predicted price → directional signal

### 4. Response System
- Final recommendation delivered via **Telegram**
  - Includes signal (`BUY / SELL / HOLD`)
  - Based on selected strategy + model + data context

### 5. Modular Design
- ✅ Async-compatible
- ✅ Easily extendable for new APIs or markets
- ✅ Separated by responsibility:
  - `controller/` — logic orchestration
  - `service/` — data processing
  - `telegram_bot/` — user interaction
  - `database/` — models + session

## ⚙️ Features

- 📊 **Two analysis modes**: 
  - **Price Direction Prediction** (Expert System)
  - **Entry/Exit Point Forecast** (Neural Networks)

- 🔍 **4 trading styles**:
  - Scalping (1-min)
  - Intraday
  - Swing
  - Investing

- 🧠 **Model evaluation**: MAE, RMSE, R², MAPE → choose the best

- 💾 **Data Sources**:
  - Binance Futures (minute-wise candles)
  - FRED (macro indicators)
  - Alternative.me (crypto sentiment, BTC dominance, supply, etc.)

- 📦 **Storage**:
  - MySQL + SQLAlchemy
  - Three key tables:
    - `crypto_tickers_data`
    - `fundamental_crypto_data`
    - `fundamental_data`

## 🧪 Technologies Used

| Tool/Tech       | Purpose                              |
|-----------------|--------------------------------------|
| Python          | Main language                        |
| aiogram         | Telegram bot                         |
| TensorFlow/Keras| ML models (LSTM, GRU, MLP)           |
| SQLAlchemy      | ORM + async DB operations            |
| MySQL           | Data persistence                     |
| Binance API     | Market data                          |
| FRED API        | Economic indicators                  |
| alternative.me  | Crypto market metrics                |