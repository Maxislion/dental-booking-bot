from aiogram import Bot, Dispatcher
import asyncio

from app.utils.config import BOT_TOKEN
from app.handlers.start import router as start_router

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)

    await dp.start_polling(bot)

def start_bot():
    asyncio.run(main())
