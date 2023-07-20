from db.connect import connect_Postgre


async def get_db():
    async_session = await connect_Postgre()
    try:
        yield async_session
    finally:
        await async_session.close()

