from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.model.db.models import crypto_tickers_data_table


async def get_all_crypto_tickers(session: AsyncSession):
    stmt = select(crypto_tickers_data_table)
    result = await session.execute(stmt)
    return result.mappings().all()


async def get_all_crypto_tickers_by_symbol(session: AsyncSession, symbol: str):
    stmt = (select(crypto_tickers_data_table)
            .where(crypto_tickers_data_table.c.symbol == symbol))
    result = await session.execute(stmt)
    return result


async def get_all_close_prices_by_symbol(session: AsyncSession, symbol: str):
    stmt = (select(crypto_tickers_data_table.c.close)
            .where(crypto_tickers_data_table.c.symbol == symbol)
            .order_by(crypto_tickers_data_table.c.timestamp))
    result = await session.execute(stmt)
    return result


async def get_all_crypto_tickers_by_symbol_and_from_timestamp(session: AsyncSession, symbol: str, start_ts: int):
    stmt = (select(crypto_tickers_data_table)
            .where(crypto_tickers_data_table.c.symbol == symbol)
            .where(crypto_tickers_data_table.c.timestamp >= start_ts)
            .order_by(desc(crypto_tickers_data_table.c.timestamp)))
    result = await session.execute(stmt)
    return result.mappings().all()


async def get_all_ohlc_by_symbol(session: AsyncSession, symbol: str):
    stmt = (
        select(
            crypto_tickers_data_table.c.open,
            crypto_tickers_data_table.c.close,
            crypto_tickers_data_table.c.high,
            crypto_tickers_data_table.c.low
        )
        .where(crypto_tickers_data_table.c.symbol == symbol)
        .order_by(crypto_tickers_data_table.c.timestamp)
    )
    result = await session.execute(stmt)
    return result
