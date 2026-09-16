import os
import sys
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db

async def seed_db():
    print("Initializing database tables...")
    await init_db()
    print("Database tables created successfully.")

if __name__ == '__main__':
    asyncio.run(seed_db())
