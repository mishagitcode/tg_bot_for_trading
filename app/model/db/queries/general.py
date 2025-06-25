from app.model.db.database import async_engine
from app.model.db.models import metadata_obj


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(metadata_obj.create_all)
