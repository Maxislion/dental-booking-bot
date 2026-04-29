from aiogram import Bot, Dispatcher
import asyncio

from app.utils.config import BOT_TOKEN
from app.handlers.start import router as start_router
from app.handlers.booking import router as booking_router
from app.handlers.services import router as services_router
from database.db import init_db
from app.services.reminder_service import reminder_loop

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(booking_router)
    dp.include_router(services_router)
    asyncio.create_task(reminder_loop(bot))

    await dp.start_polling(bot)

def start_bot():
    asyncio.run(main())


async def main():
    await init_db()  # 👈 ВАЖНО

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start_router)
    dp.include_router(booking_router)
    dp.include_router(services_router)

    await dp.start_polling(bot)