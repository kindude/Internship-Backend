from datetime import datetime
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from models.Models import Quiz, Question, Option, QuizResult, User
from repositories.action_repository import logger
from repositories.quiz_result_repository import QuizResultRepository
from repositories.redis_repository import RedisRepository
from schemas.Option import OptionResponse, OptionAddRequest, OptionUpdateScheme
from schemas.Question import QuestionListResponse, QuestionUpdateScheme, QuestionTakeQuiz
from schemas.Quiz import QuizResponse, QuestionResponse, QuizListResponse, DeleteScheme, QuizAddRequest, \
    QuizUpdateScheme


class QuizzRepository:
    def __init__(self, database: AsyncSession):
        self.async_session = database

    async def create_quizz(self, quiz: QuizAddRequest) -> QuizResponse:
        try:
            if len(quiz.questions) < 2:
                raise Exception("Each quiz must have at least 2 questions")

            for question in quiz.questions:
                if len(question.options) < 2:
                    raise Exception("Each question must have at least 2 options")

            quizToAdd = Quiz(
                title=quiz.title,
                description=quiz.description,
                frequency=quiz.frequency,
                company_id=quiz.company_id
            )
            self.async_session.add(quizToAdd)
            await self.async_session.commit()

            await self.async_session.refresh(quizToAdd)

            for question in quiz.questions:
                questionToAdd = Question(text=question.question, quiz_id=quizToAdd.id)
                self.async_session.add(questionToAdd)
                await self.async_session.commit()

                await self.async_session.refresh(questionToAdd)

                options = [
                    Option(text=option.text, question_id=questionToAdd.id, is_correct=option.is_correct)
                    for option in question.options
                ]
                self.async_session.add_all(options)
                await self.async_session.commit()

            return self.quiz_to_response(quizToAdd)

        except Exception as e:
            print("Error:", str(e))

    @staticmethod
    def quiz_to_response(quiz: Quiz) -> QuizResponse:
        return QuizResponse(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            frequency=quiz.frequency,
            company_id=quiz.company_id
        )

    @staticmethod
    def question_to_response(question: Question, options: List[OptionResponse]) -> QuestionResponse:
        return QuestionResponse(
            id=question.id,
            text=question.text,
            quiz_id=question.quiz_id,
            options=options
        )

    @staticmethod
    def option_to_response(option: Option) -> OptionResponse:
        return OptionResponse(
            id=option.id,
            text=option.text,
            question_id=option.question_id,
        )

    async def get_quiz(self, id: int) -> QuizResponse:
        try:
            query = select(Quiz).filter(Quiz.id == id)
            quiz = await self.async_session.execute(query)
            quiz = quiz.scalar_one_or_none()
            quiz_ret = self.quiz_to_response(quiz)
            if quiz_ret:
                return quiz_ret
        except Exception as e:
            print(f"Error: {e}")

    async def get_quizzes(self, company_id: int) -> QuizListResponse:
        try:
            query = select(Quiz).filter(Quiz.company_id == company_id)
            quizzes = await self.async_session.execute(query)
            quizzes = quizzes.scalars().all()
            quizzes_retrieved = []
            for quiz in quizzes:
                quiz_rep = await self.get_quiz(quiz.id)
                quizzes_retrieved.append(quiz_rep)
            return QuizListResponse(quizzes=quizzes_retrieved)

        except Exception as e:
            print(f"Error: {e}")

    async def get_questions(self, quiz_id: int) -> QuestionListResponse:
        try:
            query = select(Question).filter(Question.quiz_id == quiz_id)
            questions = await self.async_session.execute(query)
            questions = questions.scalars().all()
            questions_with_options = []

            for question in questions:
                options_query = select(Option).filter(Option.question_id == question.id)
                options = await self.async_session.execute(options_query)
                options = options.scalars().all()
                question_options = [self.option_to_response(option) for option in options]
                questions_with_options.append((question, question_options))

            questions_responses = [
                self.question_to_response(question, options)
                for question, options in questions_with_options
            ]

            return QuestionListResponse(questions=questions_responses)

        except Exception as e:
            print(f"Error: {e}")

    async def update_option(self, option: OptionUpdateScheme) -> OptionResponse:
        try:
            query = select(Option).filter(Option.id == option.id)
            option_to_update = await self.async_session.execute(query)
            option_to_update = option_to_update.scalar_one_or_none()
            if option_to_update:
                option_to_update.text = option.text
                option_to_update.is_correct = option.is_correct
                await self.async_session.commit()
            return self.option_to_response(option_to_update)
        except Exception as e:
            print(f"Error: {e}")

    async def update_question(self, question: QuestionUpdateScheme) -> QuestionResponse:
        try:
            query = select(Question).filter(Question.id == question.id)
            question_to_update = await self.async_session.execute(query)
            question_to_update = question_to_update.scalar_one_or_none()
            if question_to_update:
                question_to_update.text = question.text
                query = select(Option).filter(Option.question_id == question_to_update.id)
                options = await self.async_session.execute(query)
                options = options.scalars().all()
                options_to_resp = [self.option_to_response(option) for option in options]
                await self.async_session.commit()
                return self.question_to_response(question_to_update, options_to_resp)
        except Exception as e:
            print(f"Error: {e}")

    async def update_quiz(self, quiz: QuizUpdateScheme) -> QuizResponse:
        try:
            query = select(Quiz).filter(Quiz.id == quiz.id)
            quiz_to_update = await self.async_session.execute(query)
            quiz_to_update = quiz_to_update.scalar_one_or_none()
            if quiz_to_update:
                quiz_to_update.title = quiz.title
                quiz_to_update.description = quiz.description
                quiz_to_update.frequency = quiz.frequency
                await self.async_session.commit()
                return self.quiz_to_response(quiz_to_update)
        except Exception as e:
            print(f"Error: {e}")

    async def delete_quiz(self, quiz_id: int):
        try:
            query = select(Quiz).filter(Quiz.id == quiz_id)
            quiz = await self.async_session.execute(query)
            quiz = quiz.scalar_one_or_none()
            if not quiz:
                return DeleteScheme(
                    message="Quiz wasn't found",
                    id=-1
                )

            await self.async_session.delete(quiz)

            await self.async_session.commit()

            logger.info(f"Quiz was deleted ID: {quiz_id}")
            return DeleteScheme(
                message="Quiz was successfully deleted",
                id=quiz_id)

        except Exception as e:
            print(f"An error occurred while deleting quiz: {e}")

    async def delete_question(self, question_id: int):
        try:
            query = select(Question).filter(Question.id == question_id)
            question = await self.async_session.execute(query)
            question = question.scalar_one_or_none()
            if not question:
                return DeleteScheme(
                    message="Question wasn't found",
                    id=-1
                )

            await self.async_session.delete(question)

            await self.async_session.commit()

            logger.info(f"Question was deleted ID: {question_id}")
            return DeleteScheme(
                message="Question was successfully deleted",
                id=question_id)

        except Exception as e:
            print(f"An error occurred while deleting question: {e}")

    async def delete_option(self, option_id: int) -> DeleteScheme:
        try:
            query = select(Option).filter(Option.id == option_id)
            option = await self.async_session.execute(query)
            option = option.scalar_one_or_none()

            if not option:
                return DeleteScheme(
                    message="Option wasn't found",
                    id=-1
                )

            await self.async_session.delete(option)

            await self.async_session.commit()

            logger.info(f"Option was deleted ID: {option_id}")
            return DeleteScheme(
                message="Option was successfully deleted",
                id=option_id)

        except Exception as e:
            print(f"An error occurred while deleting option: {e}")

    async def take_quiz(self, quiz_id: int, questions: List[QuestionTakeQuiz], company_id: int, user_id: int) -> dict:
        try:
            correct_answers = 0
            total_questions = len(questions)
            query = select(Option).filter(Option.is_correct)
            correct_options = await self.async_session.execute(query)
            correct_options = correct_options.scalars().all()
            correct_options_text = {option.text for option in correct_options}
            for question in questions:
                if question.option.text in correct_options_text:
                    correct_answers += 1

            quiz_result = QuizResult(
                user_id=user_id,
                company_id=company_id,
                correct_answers=correct_answers,
                questions=total_questions,
                timestamp=datetime.utcnow(),
                quiz_id=quiz_id
            )

            self.async_session.add(quiz_result)
            await self.async_session.commit()

            quiz_result_rep = QuizResultRepository(database=self.async_session)

            user_averages = await quiz_result_rep.calculate_user_averages(user_id, company_id)

            quiz_data = {
                "user_id": user_id,
                "company_id": company_id,
                "quiz_id": quiz_id,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "time": datetime.utcnow().isoformat()
            }

            try:
                async with RedisRepository() as redis_rep:
                    await redis_rep.save_quiz(quiz_data)
                    print("Quiz data saved to Redis")
            except Exception as e:
                print(f"An error occurred while using RedisRepository: {e}")

            return {
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                **user_averages
            }

        except Exception as e:
            print(f"An error occurred while taking the quiz: {e}")





