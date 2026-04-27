import aiosqlite  # type: ignore

DB_PATH = "database.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                doctor TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
        """)
        await db.commit()