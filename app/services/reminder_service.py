import asyncio
from datetime import datetime, timedelta

from app.repositories.booking_repo import get_all_bookings, mark_notified


async def reminder_loop(bot):
    while True:
        bookings = await get_all_bookings()
        now = datetime.now()

        for booking in bookings:
            id_, user_id, doctor, dt_str, n24, n2 = booking
            booking_dt = datetime.fromisoformat(dt_str)

            diff = booking_dt - now

            if not n24 and timedelta(hours=23, minutes=59) < diff < timedelta(hours=24, minutes=1):
                await bot.send_message(
                    user_id,
                    f"⏰ Напоминание!\n\nЗавтра запись:\n👨‍⚕️ {doctor}\n⏰ {booking_dt.strftime('%H:%M')}"
                )
                await mark_notified(id_, "24h")

            if not n2 and timedelta(hours=1, minutes=59) < diff < timedelta(hours=2, minutes=1):
                await bot.send_message(
                    user_id,
                    f"⏰ Через 2 часа запись:\n👨‍⚕️ {doctor}\n⏰ {booking_dt.strftime('%H:%M')}"
                )
                await mark_notified(id_, "2h")

        await asyncio.sleep(60)