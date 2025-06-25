from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.model.db.config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_aiomysql,
    echo=True,
    future=True
)

async_session_maker = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)
