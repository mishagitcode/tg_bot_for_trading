import asyncio
from app.data.crypto_market.base import start_data_collection, assets
from app.data.crypto_market.crypto_fundamental_data import collect_fundamental_crypto_data
from app.data.fundamental_data import collect_fundamental_data
from app.model.db.queries.general import create_tables
from app.view.telegram_bot import start_bot


async def main():
    await create_tables()
    await asyncio.gather(
        collect_fundamental_data(),
        collect_fundamental_crypto_data(),
        start_bot(),
        *[start_data_collection(asset, "1m") for asset in assets]
    )

if __name__ == '__main__':
    asyncio.run(main())
