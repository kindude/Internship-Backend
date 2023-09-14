import asyncio
import os
from contextlib import asynccontextmanager

import redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_session
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from ENV import DB_URL_CONNECT

# Load environment variables
load_dotenv()


async def connect_Postgres():
    database_url = DB_URL_CONNECT
    engine = create_async_engine(database_url, future=True, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return async_session()

