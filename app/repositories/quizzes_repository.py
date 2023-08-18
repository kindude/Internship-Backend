from typing import List

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, delete, and_
from sqlalchemy.orm import selectinload

from models.Models import Quiz, Question, Option
from repositories.action_repository import logger
from schemas.Quiz import QuizScheme, QuestionScheme, OptionsListScheme, QuestionsListScheme, QuizResponse, \
    QuestionResponse, OptionResponse, QuizRequest, QuizListResponse, OptionScheme,  DeleteScheme


class QuizzRepository:
    def __init__(self, database: async_sessionmaker[AsyncSession]):
        self.async_session = database

    async def create_quizz(self, quiz: QuizRequest) -> QuizResponse:
        try:
            if len(quiz.questions) < 2:
                raise Exception
            for x in quiz.questions:
                if(len(x.options) < 2):
                    raise Exception
            async with self.async_session as session:
                quizToAdd = Quiz(title=quiz.title, description=quiz.description,
                                 frequency=quiz.frequency, company_id=quiz.company_id)
                session.add(quizToAdd)

                q = select(Quiz).filter(Quiz.title == quiz.title).limit(1)
                quiz_added = await session.execute(q)
                quiz_added = quiz_added.scalar_one_or_none()

                questions = [Question(text=question.question, quiz_id=quiz_added.id) for question in quiz.questions]


                session.add_all(questions)

                for question in quiz.questions:
                    query = select(Question).filter(Question.text == question.question).limit(1)
                    db_question = await session.execute(query)
                    db_question = db_question.scalar_one_or_none()
                    if db_question:
                        options = [
                            Option(text=option.text, question_id=db_question.id, is_correct=option.is_correct)
                            for option in question.options
                        ]
                        session.add_all(options)

                await session.commit()
                options_response = [self.option_to_response(option) for option in options]

                print(options_response)
                question_response = [self.question_to_response(question, options_response) for question in questions]
                print(question_response)
                return self.quiz_to_response(quizToAdd, question_response)


        except Exception as e:

            print("Error:", str(e))

    def quiz_to_response(self, quiz:Quiz, questions_: List[QuestionResponse]) -> QuizResponse:
        return QuizResponse(
            title=quiz.title,
            description=quiz.description,
            frequency=quiz.frequency,
            questions=questions_,
            company_id=quiz.company_id
        )
    def question_to_response(self, question:Question, options_: List[OptionResponse]) ->QuestionResponse:
        return QuestionResponse(
            question=question.text,
            quiz_id =question.quiz_id,
            options=options_
        )
    def option_to_response(self, option:Option) -> OptionResponse:
        return OptionResponse(
            text=option.text,
            question_id = option.question_id,
            is_correct = option.is_correct
        )

    async def get_quiz(self, id: int) -> QuizResponse:
        try:
            async with self.async_session as session:
                query = select(Quiz).filter(Quiz.id==id)
                quiz = await session.execute(query)
                quiz = quiz.scalar_one_or_none()

                query = select(Question).filter(Question.quiz_id == quiz.id)

                questions = await session.execute(query)
                questions = questions.scalars().all()
                questions_to_quizz = []
                for q in questions:
                    query = select(Option).filter(Option.question_id == q.id)
                    options = await session.execute(query)
                    options = options.scalars().all()
                    options_response = [self.option_to_response(option) for option in options]
                    questions_to_quizz.append(self.question_to_response(q, options_response))

                quiz_ret = self.quiz_to_response(quiz,questions_to_quizz)
                if quiz_ret is None:
                    return None
                return quiz_ret
        except Exception as e:
            print(f"Error: {e}")

    async def get_quizzes(self, company_id:int) -> QuizListResponse:
        try:
            async with self.async_session as session:
                query = select(Quiz).filter(Quiz.company_id == company_id)
                quizzes = await session.execute(query)
                quizzes = quizzes.scalars().all()
                quizzes_retrieved = []
                for quiz in quizzes:
                    quiz_rep = await self.get_quiz(quiz.id)
                    quizzes_retrieved.append(quiz_rep)

                return QuizListResponse(quizzes=quizzes_retrieved)

        except Exception as e:
            print(f"Error: {e}")


    async def update_option(self, option:OptionScheme):
        try:
            async with self.async_session as session:
                option_to_update = await session.get(Option, option.id)
                if option_to_update is not None:
                    option_to_update.text = option.text
                    option_to_update.is_correct=option.is_correct
                    session.commit()
                return self.option_to_response(option_to_update)
        except Exception as e:
            print(f"Error: {e}")

    async def update_question(self, question:QuestionScheme):
        try:
            async with self.async_session as session:
                question_to_update = await session.get(Question, question.id)
                if question_to_update is not None:
                    question_to_update.text = question.question
                    session.commit()

                return self.question_to_response(question_to_update, options_=question.options)
        except Exception as e:
            print(f"Error: {e}")


    async def update_quiz(self, quiz:QuizScheme):
        try:
            async with self.async_session as session:
                quiz_to_update = await session.get(Quiz, quiz.id)
                if quiz_to_update is not None:
                    quiz_to_update.title = quiz.title
                    quiz_to_update.description = quiz.description
                    quiz_to_update.frequency = quiz.frequency
                    return self.quiz_to_response(quiz_to_update, quiz.questions)
        except Exception as e:
            print(f"Error: {e}")


    async def delete_quiz(self, quiz_id:int):
        try:
            company = await self.get_quiz(id=quiz_id)
            if company:
                async with self.async_session as session:
                    query = delete(Quiz).where(Quiz.id == quiz_id)
                    result = await session.execute(query)
                    await session.commit()
                    if result:
                        logger.info(f"Quiz was deleted ID: {quiz_id}")
                        return DeleteScheme(
                            message="Quiz was successfully deleted",
                            id=id
                        )
                    else:
                        return DeleteScheme(
                            message="Quiz wasn't deleted",
                            id=-1
                        )
            else:
                return DeleteScheme(
                    message="Quiz wasn't deleted",
                    id=-1
                )

        except Exception as e:
            print(f"An error occurred while deleting quiz: {e}")



    async def delete_question(self, question_id:int):
        try:
            company = await self.get_quiz(id=question_id)
            if company:
                async with self.async_session as session:
                    query = delete(Question).where(Question.id == question_id)
                    result = await session.execute(query)
                    await session.commit()
                    if result:
                        logger.info(f"Question was deleted ID: {question_id}")
                        return DeleteScheme(
                            message="Question was successfully deleted",
                            id=id
                        )
                    else:
                        return DeleteScheme(
                            message="Question wasn't deleted",
                            id=-1
                        )
            else:
                return DeleteScheme(
                    message="Question wasn't deleted",
                    id=-1
                )

        except Exception as e:
            print(f"An error occurred while deleting question: {e}")

    async def delete_option(self, option_id:int):
        try:
            company = await self.get_quiz(id=option_id)
            if company:
                async with self.async_session as session:
                    query = delete(Question).where(Question.id == option_id)
                    result = await session.execute(query)
                    await session.commit()
                    if result:
                        logger.info(f"Option was deleted ID: {option_id}")
                        return DeleteScheme(
                            message="Option was successfully deleted",
                            id=id
                        )
                    else:
                        return DeleteScheme(
                            message="Option wasn't deleted",
                            id=-1
                        )
            else:
                return DeleteScheme(
                    message="Option wasn't deleted",
                    id=-1
                )

        except Exception as e:
            print(f"An error occurred while deleting option: {e}")