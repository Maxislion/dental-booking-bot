import aiosqlite  # type: ignore
from database.db import DB_PATH
from datetime import datetime, timedelta


async def create_booking(user_id, doctor, booking_datetime, pending_message_id=None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO bookings (
                user_id, doctor, booking_datetime, status, pending_message_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, doctor, booking_datetime, "pending", pending_message_id),
        )
        await db.commit()


async def get_booked_times(doctor, date):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
    SELECT booking_datetime FROM bookings 
    WHERE doctor = ? AND status != 'cancelled_by_user'
    """,
            (doctor,),
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
            (start_of_day.isoformat(), end_of_day.isoformat()),
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


from datetime import datetime


async def update_booking_status(user_id, doctor, date, time, status):
    booking_dt = datetime.strptime(f"{date} {time}", "%d.%m %H:%M")
    booking_dt = booking_dt.replace(year=datetime.now().year)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE bookings
            SET status = ?
            WHERE user_id = ? AND doctor = ? AND booking_datetime = ?
            """,
            (status, user_id, doctor, booking_dt.isoformat()),
        )
        await db.commit()


async def get_pending_message_id(user_id, doctor, date, time):
    booking_dt = datetime.strptime(f"{date} {time}", "%d.%m %H:%M")
    booking_dt = booking_dt.replace(year=datetime.now().year)

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT pending_message_id
            FROM bookings
            WHERE user_id = ? AND doctor = ? AND booking_datetime = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id, doctor, booking_dt.isoformat()),
        )
        row = await cursor.fetchone()

    return row[0] if row else None
