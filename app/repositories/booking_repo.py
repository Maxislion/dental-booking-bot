import aiosqlite  # type: ignore
from database.db import DB_PATH
from datetime import datetime, timedelta


async def create_booking(user_id, doctor, booking_datetime):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bookings (user_id, doctor, booking_datetime) VALUES (?, ?, ?)",
            (user_id, doctor, booking_datetime),
        )
        await db.commit()


async def get_booked_times(doctor, date):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT booking_datetime FROM bookings WHERE doctor = ?", (doctor,)
        )
        rows = await cursor.fetchall()

    times = []

    for row in rows:
        try:
            dt = datetime.fromisoformat(row[0])
        except Exception:
            continue  # пропускаем кривые данные

        if dt.strftime("%d.%m") == date:
            times.append(dt.strftime("%H:%M"))

    return times


async def get_all_bookings():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, user_id, doctor, booking_datetime, notified_24h, notified_2h FROM bookings"
        )
        return await cursor.fetchall()


async def get_today_bookings():
    now = datetime.now()

    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT user_id, doctor, booking_datetime
            FROM bookings
            WHERE booking_datetime >= ? AND booking_datetime < ?
            ORDER BY booking_datetime
            """,
            (start_of_day.isoformat(), end_of_day.isoformat())
        )
        return await cursor.fetchall()


async def get_all_bookings_full():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, doctor, date, time FROM bookings")
        return await cursor.fetchall()


async def mark_notified(booking_id, type_):
    async with aiosqlite.connect(DB_PATH) as db:
        if type_ == "24h":
            await db.execute(
                "UPDATE bookings SET notified_24h = 1 WHERE id = ?", (booking_id,)
            )
        elif type_ == "2h":
            await db.execute(
                "UPDATE bookings SET notified_2h = 1 WHERE id = ?", (booking_id,)
            )
        await db.commit()
