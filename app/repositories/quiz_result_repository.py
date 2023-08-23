from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.Models import QuizResult
from schemas.QuizResult import QuizResultAddRequest


class QuizResultRepository:
    def __init__(self, database: AsyncSession):
        self.async_session = database

    async def create_quiz_result(self, quizResult: QuizResultAddRequest):
        try:
            self.async_session.add(quizResult.model_dump())
            await self.async_session.commit()
            return quizResult
        except Exception as e:
            print(f"An error occurred while creating the user: {e}")
            raise e

    async def calculate_user_averages(self, user_id: int, company_id: int):
        try:

            company_query = select(func.avg(QuizResult.correct_answers).label("average_company_rating")).where(
                QuizResult.user_id == user_id, QuizResult.company_id == company_id)
            average_company_rating = await self.async_session.execute(company_query)
            average_company_rating = average_company_rating.scalar_one_or_none()

            system_query = select(func.avg(QuizResult.correct_answers).label("average_system_rating")).where(
                QuizResult.user_id == user_id)
            average_system_rating = await self.async_session.execute(system_query)
            average_system_rating = average_system_rating.scalar_one_or_none()

            return {
                "average_company_rating": average_company_rating,
                "average_system_rating": average_system_rating
            }

        except Exception as e:
            print(f"An error occurred while calculating user averages: {e}")