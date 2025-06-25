from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from app.model.db.models import users_table


async def create_user(session: AsyncSession, user_id: int, user_name: str) -> None:
    stmt = select(users_table.c.user_id).where(users_table.c.telegram_user_id == user_id)
    result = await session.execute(stmt)
    if result.first() is None:
        stmt = insert(users_table).values(
            telegram_user_id=user_id,
            telegram_user_name=user_name
        )
        await session.execute(stmt)
        await session.commit()


async def get_user(session: AsyncSession, user_id: int) -> dict | None:
    stmt = select(users_table).where(users_table.c.telegram_user_id == user_id)
    result = await session.execute(stmt)
    return result.mappings().first()


async def user_update(session: AsyncSession, user_id: int, field: str, value: str) -> None:
    if field not in {"market", "result_type", "trading_style", "mode"}:
        raise ValueError("Invalid field name")
    stmt = (
        update(users_table)
        .where(users_table.c.telegram_user_id == user_id)
        .values({field: value})
    )
    await session.execute(stmt)
    await session.commit()


async def delete_user(session: AsyncSession, user_id: int) -> None:
    stmt = delete(users_table).where(users_table.telegram_user_id == user_id)
    await session.execute(stmt)
    await session.commit()
