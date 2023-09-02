from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # Изменено на AsyncIOScheduler
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db
from models.Models import Quiz, User, QuizResult, Notification


async def send_notifications(db: AsyncSession = Depends(get_db)):
    current_time = datetime.utcnow()

    async with db.begin() as conn:
        query = select(Quiz)
        quizzes = await conn.execute(query)
        quizzes = quizzes.scalars().all()
        print(quizzes)

        for quiz in quizzes:
            users_passed_quiz = conn.query(User).join(QuizResult).filter(
                QuizResult.quiz_id == quiz.id,
                QuizResult.timestamp >= (current_time - timedelta(days=quiz.frequency))
            ).all()

            for user in users_passed_quiz:
                last_completion = user.get_last_quiz_completion(quiz.id)
                if not last_completion or last_completion.timestamp < (current_time - timedelta(days=quiz.frequency)):
                    notification = Notification(
                        text=f"Вы не проходили квиз '{quiz.title}' в течение {quiz.frequency} дней!",
                        status="UNREAD",
                        quiz_id=quiz.id,
                    )
                    conn.add(notification)

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()  # Изменено на AsyncIOScheduler

    scheduler.add_job(send_notifications, 'cron', hour=16, minute=59, args=(get_db(),))

    scheduler.start()

    try:
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
