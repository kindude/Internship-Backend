from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from models.Models import QuizResult


class QuizResultRepository:
    def __init__(self, database: AsyncSession):
        self.async_session = database

    async def create_quiz_result(self, quiz_id: int, company_id: int, user_id: int, correct_answers: int,
                                 total_questions: int):
        try:
            now = datetime.now()
            quiz_result = QuizResult(
                company_id=company_id,
                user_id=user_id,
                quiz_id=quiz_id,
                correct_answers=correct_answers,
                questions=total_questions,
                timestamp=now
            )
            self.async_session.add(quiz_result)
            await self.async_session.commit()
            return correct_answers, total_questions

        except Exception as e:
            print(f"An error occurred while creating the quiz result: {e}")
            raise e