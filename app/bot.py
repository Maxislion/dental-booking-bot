from aiogram import Bot, Dispatcher
import asyncio
from app.utils.config import BOT_TOKEN

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    await dp.start_polling(bot)

def start_bot():
    asyncio.run(main())
