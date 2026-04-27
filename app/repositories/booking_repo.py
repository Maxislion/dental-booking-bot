import aiosqlite # type: ignore
from database.db import DB_PATH
from datetime import datetime


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
    
async def get_all_bookings():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, doctor, date, time FROM bookings ORDER BY id DESC LIMIT 10"
        )
        return await cursor.fetchall()
    
async def get_today_bookings():
    today = datetime.today().strftime("%d.%m")

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT user_id, doctor, date, time FROM bookings WHERE date = ? ORDER BY time",
            (today,)
        )
        return await cursor.fetchall()