import asyncio
from sqlalchemy import select, and_
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, aliased
from contextlib import asynccontextmanager
from ENV import DB_URL_CONNECT, DB_URL_CONNECT_SCRIPT
from models.Models import Quiz, User, QuizResult, Notification
from sqlalchemy import cast, DateTime

from repositories.quiz_result_repository import QuizResultRepository


@asynccontextmanager
async def connect_to_postgres():
    database_url = DB_URL_CONNECT_SCRIPT
    engine = create_async_engine(database_url, future=True, echo=True)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def send_notifications():
    current_time = datetime.utcnow()

    async with connect_to_postgres() as session:
        query = select(Quiz)
        quizzes = await session.execute(query)
        quizzes = quizzes.scalars().all()

        for quiz in quizzes:

            query = (
                select(User)
                .join(QuizResult, and_(
                    User.id == QuizResult.user_id,
                    QuizResult.quiz_id == quiz.id,
                    cast(QuizResult.timestamp, DateTime) <= (current_time - timedelta(days=quiz.frequency))
                ))
            )

            users_passed_quiz = await session.execute(query)
            users_passed_quiz = users_passed_quiz.scalars().all()

            for user in users_passed_quiz:
                quiz_result_repo = QuizResultRepository(database=session)
                last_completions = await quiz_result_repo.get_last_quiz_completion(user.id)
                for last_completion in last_completions:
                    last_completion_time = last_completion
                    print(last_completion_time)
                    if not last_completion_time or last_completion_time < (
                            current_time - timedelta(days=quiz.frequency)):
                        notification = Notification(
                            text=f"Вы не проходили квиз '{quiz.title}' в течение {quiz.frequency} дней!",
                            status="UNREAD",
                            user_id=user.id,
                        )
                        session.add(notification)
                        await session.commit()

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_notifications, 'interval', hours=24)

    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
