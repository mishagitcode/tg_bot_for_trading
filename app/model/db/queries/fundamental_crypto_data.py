from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.model.db.models import fundamental_crypto_data_table


async def get_all_fundamental_crypto_data(session: AsyncSession):
    stmt = select(fundamental_crypto_data_table)
    result = await session.execute(stmt)
    return result.mappings().all()


async def get_fear_and_greed_index_by_date(session: AsyncSession, date_input: date):
    stmt = (select(fundamental_crypto_data_table.c.fear_greed_index)
            .where(fundamental_crypto_data_table.c.date == date_input))
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
