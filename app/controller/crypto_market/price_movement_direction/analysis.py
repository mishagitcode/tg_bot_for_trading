from sqlalchemy.ext.asyncio import AsyncSession
from app.controller.crypto_market.price_movement_direction.intraday import intraday_analysis
from app.controller.crypto_market.price_movement_direction.investing import investing_analysis
from app.controller.crypto_market.price_movement_direction.swing import swing_analysis
from app.controller.crypto_market.price_movement_direction.scalping import scalping_analysis


async def price_movement_direction_analysis(symbol: str, trading_style: str, session: AsyncSession) -> str:
    if trading_style == "scalping":
        return await scalping_analysis(symbol, session)
    if trading_style == "intraday":
        return await intraday_analysis(symbol, session)
    if trading_style == "swing":
        return await swing_analysis(symbol, session)
    if trading_style == "investing":
        return await investing_analysis(symbol, session)
