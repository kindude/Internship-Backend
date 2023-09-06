import asyncio
from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, aliased
from contextlib import asynccontextmanager
from ENV import DB_URL_CONNECT, DB_URL_CONNECT_SCRIPT
from models.Models import Quiz, User, QuizResult, Notification

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
        # Выбираем все квизы из таблицы Quiz
        query = select(Quiz)
        quizzes = await session.execute(query)
        quizzes = quizzes.scalars().all()

        for quiz in quizzes:
            # Определяем алиасы для таблиц
            user_alias = aliased(User)
            quiz_result_alias = aliased(QuizResult)

            # Создаем запрос с использованием SQLAlchemy для JOIN
            query = (
                select(User)
                .join(quiz_result_alias, User.id == quiz_result_alias.user_id)
                .filter(
                    quiz_result_alias.quiz_id == quiz.id,
                    quiz_result_alias.timestamp >= (current_time - timedelta(days=quiz.frequency))
                )
            )

            # Выполняем запрос и получаем результат
            users_passed_quiz = await session.execute(query)
            users_passed_quiz = users_passed_quiz.scalars().all()

            for user in users_passed_quiz:
                last_completion = user.get_last_quiz_completion(quiz.id)
                if not last_completion or last_completion.timestamp < (current_time - timedelta(days=quiz.frequency)):
                    notification = Notification(
                        text=f"Вы не проходили квиз '{quiz.title}' в течение {quiz.frequency} дней!",
                        status="UNREAD",
                        quiz_id=quiz.id,
                    )
                    session.add(notification)

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()

    scheduler.add_job(send_notifications, 'interval', hours=24)

    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
