from typing import List

from sqlalchemy import select, func, distinct, text, cast, Date, and_, distinct, desc, over
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from models.Models import QuizResult, User
from schemas.Company import CompanyUserLastCompletion, ListCompanyUserLastCompletion
from schemas.Quiz import LastQuizCompletion, ListLastQuizCompletion
from schemas.QuizResult import QuizResultAddRequest, QuizAverage, UserQuizAveragesResponse, Average
from schemas.User import ListUsersAverages, UsersAverage


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
                company_query = select(func.avg((QuizResult.correct_answers/QuizResult.questions * 5)).label("average_company_rating")).where(
                    QuizResult.user_id == user_id, QuizResult.company_id == company_id)
                average_company_rating = await self.async_session.execute(company_query)
                average_company_rating = average_company_rating.scalar_one_or_none()

            system_query = select(func.avg((QuizResult.correct_answers/QuizResult.questions * 5)).label("average_system_rating")).where(
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

    async def get_last_quiz_completion(self, user_id: int) -> ListLastQuizCompletion:
        try:
            last_completion_query = select(
                QuizResult.quiz_id.label("quiz_id"),
                func.max(QuizResult.timestamp).label("last_completion_time")
            ).where(QuizResult.user_id == user_id).group_by(QuizResult.quiz_id)

            last_completions = await self.async_session.execute(last_completion_query)
            results = last_completions.fetchall()

            completions = [LastQuizCompletion(quiz_id=row[0], last_completion_time=row[1].strftime('%d/%m')) for row in
                    results]
            return ListLastQuizCompletion(completions=completions)

        except Exception as e:
            print(f"An error occurred while fetching last quiz completions: {e}")

    async def get_all_users_averages(self, company_id: int) -> ListUsersAverages:
        try:
            query = select(QuizResult).where(QuizResult.company_id == company_id)
            results = await self.async_session.execute(query)
            user_averages = results.scalars().all()

            averages = []

            total_questions = 0
            correct_questions = 0

            for user_average in user_averages:
                user_id = str(user_average.user_id) + " " + str(user_average.timestamp)
                total_questions += user_average.questions
                correct_questions += user_average.correct_answers

                if total_questions > 0:
                    average_score = correct_questions / total_questions * 5
                    time = str(user_average.timestamp)
                    user_average_data = UsersAverage(user_id=user_id, average=average_score, time=time)
                    averages.append(user_average_data)

            return ListUsersAverages(averages=averages)

        except Exception as e:
            print(f"An error occurred while fetching average scores over time: {e}")

    def math(self, result) -> List[Average]:
        averages = {}

        for quiz_average in result:
            quiz_id = quiz_average.quiz_id
            if quiz_id not in averages:
                averages[quiz_id] = {
                    "quiz_id": quiz_id,
                    "average": "",
                    "timestamp": "",
                    "total_questions": 0,
                    "total_correct_answers": 0
                }

            total_questions = averages.get(quiz_id, {}).get("total_questions", 0)
            correct_questions = averages.get(quiz_id, {}).get("total_correct_answers", 0)

            total_questions += quiz_average.questions
            correct_questions += quiz_average.correct_answers

            if total_questions > 0:
                average = correct_questions / total_questions * 5
                if averages.get(quiz_id, {}).get("average"):
                    averages[quiz_id]["average"] += f", {average}"
                else:
                    averages[quiz_id]["average"] = str(average)

            if averages.get(quiz_id, {}).get("timestamp"):
                averages[quiz_id]["timestamp"] += f", {quiz_average.timestamp.strftime('%d/%m')}"
            else:
                averages[quiz_id]["timestamp"] = quiz_average.timestamp.strftime('%d/%m')

            averages[quiz_id]["total_questions"] = total_questions
            averages[quiz_id]["total_correct_answers"] = correct_questions

        average_objects = [Average(**values) for values in averages.values()]

        return average_objects

    async def get_my_averages(self, user_id: int) -> UserQuizAveragesResponse:
        try:
            query = select(QuizResult).where(QuizResult.user_id == user_id)
            result = await self.async_session.execute(query)
            result = result.scalars().all()
            averages = self.math(result=result)

            quiz_averages = [QuizAverage(Avges={value.quiz_id: value.dict() for value in averages})]

            return UserQuizAveragesResponse(averages=quiz_averages)

        except Exception as e:
            print(f"An error occurred while fetching average scores over time: {e}")

    async def get_user_quiz_averages(self, user_id: int, company_id: int) -> UserQuizAveragesResponse:
        try:
            query = select(QuizResult).where(and_(QuizResult.user_id == user_id, QuizResult.company_id == company_id))
            result = await self.async_session.execute(query)
            result = result.scalars().all()
            averages = self.math(result=result)

            quiz_averages = [QuizAverage(Avges={value.quiz_id: value.dict() for value in averages})]

            return UserQuizAveragesResponse(averages=quiz_averages)

        except Exception as e:
            print(f"No data found for the specified conditions. {e}")

    async def get_company_users_last_completion(self, company_id: int) -> ListCompanyUserLastCompletion:
        try:
            last_completion_query = select(
                QuizResult.user_id,
                func.max(QuizResult.timestamp).label("last_completion_time")
            ).where(QuizResult.company_id == company_id).group_by(QuizResult.user_id)

            last_completions = await self.async_session.execute(last_completion_query)
            results = last_completions.fetchall()

            last_completion_data = [
                CompanyUserLastCompletion(user_id=row[0], last_completion_time=row[1]) for row in results
            ]

            return ListCompanyUserLastCompletion(last_completions=last_completion_data)

        except Exception as e:
            print(f"An error occurred while fetching company users' last completions: {e}")

