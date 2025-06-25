import os
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from app.model.db.database import async_session_maker
from app.controller.crypto_market.price_movement_direction.analysis import price_movement_direction_analysis
from app.controller.crypto_market.point_of_entry_and_exit.analysis import point_of_entry_and_exit
from app.data.crypto_market.base import assets
from app.model.db.queries.users import create_user, get_user, user_update

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

txt = """
----------------------------------------------------------------------------------------------------

🌎 <b>Ринок</b> - фінансовий ринок, на якому бот буде здійснювати аналіз:

💰 <i>сrypto</i> (ринок криптовалют)
🏷️ <i>stocks</i> (ринок акцій)
💳 <i>bonds</i> (ринок облігацій)

----------------------------------------------------------------------------------------------------

📊 <b>Тип результату</b> - це параметр, який вказує, який тип аналізу буде проводитися:

📈 <i>price movement direction</i> (аналіз напряму руху ціни)
🎯 <i>point of entry and exit</i> (визначення точок входу та виходу з ринку з позиції)

----------------------------------------------------------------------------------------------------

💼 <b>Торговий стиль</b> - це параметр, який визначає стратегію торгівлі:

⚡ <i>scalping</i> (короткострокова торгівля з відкриттям і закриттям угод у межах кількох хвилин)
⏳ <i>intraday</i> (торгівля в межах одного дня, угоди відкриваються та закриваються в той же день)
📌 <i>swing</i> (середньострокова торгівля, де угоди тривають від кількох днів до кількох тижнів)
🏦 <i>investing</i> (довгострокове інвестування, угоди можуть тривати місяцями або навіть роками)

----------------------------------------------------------------------------------------------------

⚙️ <b>Режим</b> - це параметр, що визначає, режим роботи з ботом:

📎 <i>manual</i> (ви надсилаєте назву тікера, і отримуєте аналіз на свій запит)
🤖 <i>auto</i> (бот автоматично 24/7 надсилає аналіз, коли на ринку з'являється відповідна ситуація)

----------------------------------------------------------------------------------------------------

Напишіть /start для продовження
"""


@dp.message(F.content_type.in_({"photo", "video", "audio", "document", "sticker", "voice", "location", "contact"}))
async def handle_non_text(message: Message):
    await message.answer("⚠️ Ви не можете надсилати інформацію цього типу")
    await handle_start(message)


@dp.message(CommandStart())
async def handle_start(message: Message):
    async with async_session_maker() as session:
        await create_user(session, message.from_user.id, message.from_user.username)
        user = await get_user(session, message.from_user.id)

        if not user or any(user.get(field) is None for field in ("market", "result_type", "trading_style", "mode")):
            await message.answer("⚙️ Перед початком роботи налаштуйте бота у /settings")
        else:
            await message.answer("Напишіть тікер \n\n<em>Приклад: btc</em>")


@dp.message(Command("list"))
async def handle_settings(message: Message):
    result = ""
    for asset in assets:
        result += "- " + asset.replace("USDT", "") + "\n"
    await message.answer(f"Список доступних тікерів:\n\n{result}")


@dp.message(Command("settings"))
async def handle_settings(message: Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Інформація про налаштування", callback_data="info")],
        [InlineKeyboardButton(text="🌎 Ринок", callback_data="market"),
         InlineKeyboardButton(text="📊 Тип результату", callback_data="result_type")],
        [InlineKeyboardButton(text="💼 Торговий стиль", callback_data="style"),
         InlineKeyboardButton(text="⚙️ Режим", callback_data="mode")]
    ])

    async with async_session_maker() as session:
        user = await get_user(session, message.from_user.id) or {}

    def safe(val): return val if val is not None else "не задано"

    await message.answer(
        f"Поточні налаштування: \n\n"
        f"Ринок: <em>{safe(user.get('market'))}</em>\n"
        f"Тип результату: <em>{safe(user.get('result_type'))}</em>\n"
        f"Торговий стиль: <em>{safe(user.get('trading_style'))}</em>\n"
        f"Режим: <em>{safe(user.get('mode'))}</em>",
        reply_markup=markup
    )


@dp.callback_query()
async def handle_settings_callback(callback: CallbackQuery):
    data = callback.data
    markup = InlineKeyboardMarkup(inline_keyboard=[])

    if data == "info":
        await callback.message.answer(txt, reply_markup=markup)

    elif data == "market":
        markup.inline_keyboard.append([InlineKeyboardButton(text="💰 crypto", callback_data="crypto")])
        await callback.message.answer("Оберіть ринок:", reply_markup=markup)

    elif data == "result_type":
        markup.inline_keyboard.append([InlineKeyboardButton(
            text="📈 price movement direction",
            callback_data="price movement direction"
        )])
        markup.inline_keyboard.append([InlineKeyboardButton(
            text="🎯 point of entry and exit",
            callback_data="point of entry and exit"
        )])
        await callback.message.answer("Оберіть тип результату:", reply_markup=markup)

    elif data == "style":
        markup.inline_keyboard.extend([
            [InlineKeyboardButton(text="⚡ scalping", callback_data="scalping"),
             InlineKeyboardButton(text="⏳ intraday", callback_data="intraday")],
            [InlineKeyboardButton(text="📌 swing", callback_data="swing"),
             InlineKeyboardButton(text="🏦 investing", callback_data="investing")]
        ])
        await callback.message.answer("Оберіть торговий стиль:", reply_markup=markup)

    elif data == "mode":
        markup.inline_keyboard.append([InlineKeyboardButton(text="📎 manual", callback_data="manual")])
        await callback.message.answer("Оберіть режим:", reply_markup=markup)

    field_map = {
        "crypto": "market",
        "price movement direction": "result_type",
        "point of entry and exit": "result_type",
        "scalping": "trading_style",
        "intraday": "trading_style",
        "swing": "trading_style",
        "investing": "trading_style",
        "manual": "mode",
        "auto": "mode"
    }

    if data in field_map:
        field = field_map[data]
        async with async_session_maker() as session:
            await user_update(session, callback.from_user.id, field, data)
        await callback.message.answer(f"✅ Встановлено: <b>{data}</b>\n\nНапишіть /start для продовження")
        await callback.answer()


@dp.message(F.text)
async def handle_text(message: Message):
    ticker_input = message.text.upper()
    ticker = ticker_input if ticker_input.endswith("USDT") else ticker_input + "USDT"

    async with async_session_maker() as session:
        user = await get_user(session, message.from_user.id)

        if not user or any(user.get(field) is None for field in ("market", "result_type", "trading_style", "mode")):
            await message.answer("⚙️ Перед початком роботи налаштуйте бота у /settings")
            return

        if ticker not in assets:
            await message.answer("⚠️ Такого тікера не існує")
            return

        await message.answer("⏳ Зачекайте, будь ласка, проводиться аналіз...")

        if user["result_type"] == "price movement direction":
            analysis = await price_movement_direction_analysis(ticker, user.get("trading_style"), session)
        else:
            analysis = await point_of_entry_and_exit(ticker, user.get("trading_style"), session)

        await message.answer(analysis)
        await handle_start(message)


async def start_bot():
    print("Launching the bot...")
    await dp.start_polling(bot)
