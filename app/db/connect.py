import asyncio
import redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def connect_Postgre():
    # Postgres connection
    database_url = 'postgresql+asyncpg://kindude:1234@internship-postgres-1:5432/pg'
    engine = create_async_engine(database_url, future=True, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()


async def main():
    async_session = await connect_Postgre()

    r = redis.Redis(host="127.0.0.1", port=6379)

# Run the main function using asyncio.run()
asyncio.run(main())
