import aiosqlite

DB_PATH = "database.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                doctor TEXT,
                date TEXT,
                time TEXT
            )
        """)
        await db.commit()