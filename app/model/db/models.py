from sqlalchemy import Table, Column, Integer, MetaData, VARCHAR, String, Float, BigInteger, Date

metadata_obj = MetaData()

users_table = Table(
    "users",
    metadata_obj,
    Column("user_id", Integer, primary_key=True, unique=True, autoincrement=True),
    Column("telegram_user_id", BigInteger),
    Column("telegram_user_name", VARCHAR(64)),
    Column("market", VARCHAR(64)),
    Column("result_type", VARCHAR(64)),
    Column("trading_style", VARCHAR(64)),
    Column("mode", VARCHAR(64)),
)

crypto_tickers_data_table = Table(
    "crypto_tickers_data",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("symbol", String(16)),
    Column("timestamp", BigInteger),
    Column("open", Float),
    Column("close", Float),
    Column("high", Float),
    Column("low", Float),
    Column("quote_asset_volume", Float),
    Column("number_of_trades", Integer),
    Column("sum_open_interest", Float),
    Column("sum_open_interest_value", Float)
)

fundamental_data_table = Table(
    "fundamental_data",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("date", Date, unique=True),

    # Базові
    Column("cpi", Float),  # Consumer Price Index (1982–1984 = 100)
    Column("fed_rate", Float),  # Effective Federal Funds Rate (%)
    Column("m2_global_money_supply", Float),  # M2 Money Stock (Billions of $)
    Column("us_debt", Float),  # Total Public Debt (Millions of $)
    Column("vix_index", Float),  # CBOE Volatility Index
    Column("treasury_yield_10y", Float),  # 10-Year Treasury Yield (%)

    # Економічна активність
    Column("real_gdp", Float),  # Real GDP (Billions of chained 2012 $)
    Column("unemployment_rate", Float),  # Unemployment Rate (%)
    Column("nonfarm_payrolls", Float),  # Nonfarm Payrolls (Thousands)
    Column("industrial_production", Float),  # Industrial Production Index (2017=100)

    # Грошово-кредитна політика
    Column("m1_money_stock", Float),  # M1 Money Stock (Billions of $)
    Column("fed_target_rate_upper", Float),  # Federal Funds Target Rate – Upper Bound (%)
    Column("total_consumer_credit", Float),  # Total Consumer Credit (Billions of $)
    Column("mortgage_rate_30y", Float),  # 30-Year Fixed Mortgage Rate (%)

    # Бюджет
    Column("federal_debt_to_gdp", Float),  # Federal Debt as % of GDP

    # Ринки
    Column("sp500_index", Float),  # S&P 500 Index
    Column("vxo_index", Float),  # VXO Volatility Index (old VIX)
    Column("treasury_yield_2y", Float),  # 2-Year Treasury Yield (%)
    Column("treasury_yield_5y", Float),  # 5-Year Treasury Yield (%)
    Column("yield_curve_10y_2y", Float),  # 10Y minus 2Y Treasury Spread (%)

    # Інфляція
    Column("core_cpi", Float),  # Core CPI (CPI excluding food & energy)
    Column("ppi_all_commodities", Float),  # Producer Price Index (All Commodities)
    Column("import_price_index", Float),  # Import Price Index (Index)

    # Торгівля
    Column("trade_balance", Float),  # Trade Balance (Millions of $)
    Column("exports", Float),  # Exports of Goods & Services (Billions of $)
    Column("imports", Float),  # Imports of Goods & Services (Billions of $)

    # Нерухомість
    Column("home_price_index", Float),  # S&P/Case-Shiller Home Price Index (Index)
    Column("new_home_sales", Float),  # New Home Sales (Thousands)
    Column("housing_starts", Float),  # Housing Starts (Thousands)
)

fundamental_crypto_data_table = Table(
    "fundamental_crypto_data",
    metadata_obj,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("date", Date, unique=True),
    Column("fear_greed_index", Float),
    Column("btc_market_cap", Float),
    Column("eth_market_cap", Float),
    Column("total1", Float),  # Total market cap
    Column("total2", Float),  # Total market cap excluding BTC
    Column("total3", Float),  # Total market cap excluding BTC and ETH
)
