import aiosqlite # type: ignore
from database.db import DB_PATH


async def create_booking(user_id, doctor, date, time):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO bookings (user_id, doctor, date, time) VALUES (?, ?, ?, ?)",
            (user_id, doctor, date, time)
        )
        await db.commit()
    

async def get_booked_times(doctor, date):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT time FROM bookings WHERE doctor = ? AND date = ?",
            (doctor, date)
        )
        rows = await cursor.fetchall()
        return [row[0] for row in rows]