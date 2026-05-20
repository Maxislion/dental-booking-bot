import aiosqlite  # type: ignore

DB_PATH = "database.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        doctor TEXT NOT NULL,
        booking_datetime TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        pending_message_id INTEGER,
        notified_24h INTEGER DEFAULT 0,
        notified_2h INTEGER DEFAULT 0
        )
        """)

        cursor = await db.execute("PRAGMA table_info(bookings)")
        columns = {row[1] for row in await cursor.fetchall()}

        if "pending_message_id" not in columns:
            await db.execute(
                "ALTER TABLE bookings ADD COLUMN pending_message_id INTEGER"
            )

        await db.commit()
