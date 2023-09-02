from sqlalchemy import select, func, distinct, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

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

    async def calculate_user_averages(self, user_id: int, company_id: int = 0):
        try:
            average_company_rating = 0
            if company_id != 0:
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

    async def get_quiz_averages(self):
        try:

            average_query = select(
                QuizResult.quiz_id,
                func.avg(QuizResult.correct_answers).label("average_score"),
                func.max(QuizResult.timestamp).label("timestamp")
            ).group_by(QuizResult.quiz_id)

            averages = await self.async_session.execute(average_query)
            return [dict(row) for row in averages]

        except Exception as e:
            print(f"An error occurred while fetching quiz averages: {e}")

    async def get_last_quiz_completion(self, user_id: int):
        try:
            last_completion_query = select(
                QuizResult.quiz_id,
                func.max(QuizResult.timestamp).label("last_completion_time")
            ).where(QuizResult.user_id == user_id).group_by(QuizResult.quiz_id)

            last_completions = await self.async_session.execute(last_completion_query)
            return [dict(row) for row in last_completions]

        except Exception as e:
            print(f"An error occurred while fetching last quiz completions: {e}")

    async def get_all_users_averages(self, company_id: int):
        try:
            sql_query = text("""
                SELECT
                    timestamp,
                    user_id,
                    AVG(correct_answers) AS average_score
                FROM
                    quiz_results
                WHERE
                    company_id = :company_id
                GROUP BY
                    timestamp, user_id
            """)

            results = await self.async_session.execute(sql_query, {"company_id": company_id})
            rows = results.fetchall()

            user_averages = []
            for row in rows:
                user_average = {
                    "timestamp": row[0],
                    "user_id": row[1],
                    "average_score": row[2]
                }
                user_averages.append(user_average)

            return user_averages

        except Exception as e:
            print(f"An error occurred while fetching average scores over time: {e}")

    async def get_user_quiz_averages(self, user_id: int):
        try:
            average_query = select(
                QuizResult.quiz_id,
                func.avg(QuizResult.correct_answers).label("average_score")
            ).where(QuizResult.user_id == user_id).group_by(QuizResult.quiz_id)

            averages = await self.async_session.execute(average_query)
            return [dict(row) for row in averages]

        except Exception as e:
            print(f"An error occurred while fetching user's quiz averages: {e}")

    async def get_company_users_last_completion(self, company_id: int):
        try:
            last_completion_query = select(
                QuizResult.user_id,
                func.max(QuizResult.timestamp).label("last_completion_time")
            ).where(QuizResult.company_id == company_id).group_by(QuizResult.user_id)

            last_completions = await self.async_session.execute(last_completion_query)
            return [dict(row) for row in last_completions]

        except Exception as e:
            print(f"An error occurred while fetching company users' last completions: {e}")