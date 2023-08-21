

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from models.Models import Quiz, Question, Option, QuizResult, User, CompanyRating
from repositories.action_repository import logger
from repositories.quiz_result_repository import QuizResultRepository
from schemas.Quiz import  QuestionScheme, OptionsListScheme, QuestionsListScheme, QuizResponse, \
    QuestionResponse, OptionResponse, QuizRequest, QuizListResponse, OptionScheme, DeleteScheme, QuestionListResponse


class QuizzRepository:
    def __init__(self, database: AsyncSession):
        self.async_session = database

    async def create_quizz(self, quiz: QuizRequest) -> QuizResponse:
        try:
            if len(quiz.questions) < 2:
                raise Exception
            for x in quiz.questions:
                if(len(x.options) < 2):
                    raise Exception

            quizToAdd = Quiz(title=quiz.title, description=quiz.description,
                             frequency=quiz.frequency, company_id=quiz.company_id)
            self.async_session.add(quizToAdd)

            q = select(Quiz).filter(Quiz.title == quiz.title).limit(1)
            quiz_added = await self.async_session.execute(q)
            quiz_added = quiz_added.scalar_one_or_none()

            questions = [Question(text=question.question, quiz_id=quiz_added.id) for question in quiz.questions]


            self.async_session.add_all(questions)

            for question in quiz.questions:
                query = select(Question).where(Question.text == question.question).limit(1)
                db_question = await self.async_session.execute(query)
                db_question = db_question.scalar_one_or_none()
                if db_question:
                    options = [
                        Option(text=option.text, question_id=db_question.id, is_correct=option.is_correct)
                        for option in question.options
                    ]

                    self.async_session.add_all(options)

            await self.async_session.commit()
            options_response = [self.option_to_response(option) for option in options]

            print(options_response)
            question_response = [self.question_to_response(question, options_response) for question in questions]
            print(question_response)
            return self.quiz_to_response(quizToAdd)

        except Exception as e:
            print("Error:", str(e))

    @staticmethod
    def quiz_to_response(self, quiz:Quiz) -> QuizResponse:
        return QuizResponse(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            frequency=quiz.frequency,
            company_id=quiz.company_id
        )

    @staticmethod
    def question_to_response(self, question:Question) ->QuestionResponse:
        print(question.text, question.quiz_id)
        return QuestionResponse(
            question=question.text,
            quiz_id=question.quiz_id
        )
    @staticmethod
    def option_to_response(self, option:Option) -> OptionResponse:
        return OptionResponse(
            text=option.text,
            question_id = option.question_id,
            is_correct = option.is_correct
        )

    async def get_quiz(self, id: int) -> QuizResponse:
        try:
            query = select(Quiz).filter(Quiz.id == id)
            quiz = await self.async_session.execute(query)
            quiz = quiz.scalar_one_or_none()

            query = select(Question).filter(Question.quiz_id == quiz.id)

            # questions = await session.execute(query)
            # questions = questions.scalars().all()
            # questions_to_quizz = []
            # for q in questions:
            #     query = select(Option).filter(Option.question_id == q.id)
            #     options = await session.execute(query)
            #     options = options.scalars().all()
            #     options_response = [self.option_to_response(option) for option in options]
            #     questions_to_quizz.append(self.question_to_response(q, options_response))

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
            questions = [self.question_to_response(question) for question in questions]

            return QuestionListResponse(questions=questions)

        except Exception as e:
            print(f"Error: {e}")

    async def update_option(self, option:OptionScheme):
        try:
            option_to_update = await self.async_session.get(Option, option.id)
            option_to_update = option_to_update.scalar_one_or_none()
            if option_to_update is not None:
                option_to_update.text = option.text
                option_to_update.is_correct = option.is_correct
                await self.async_session.commit()
            return self.option_to_response(option_to_update)
        except Exception as e:
            print(f"Error: {e}")

    async def update_question(self, question:QuestionScheme):
        try:
            question_to_update = await self.async_session.get(Question, question.id)
            question_to_update = question_to_update.scalars_one_or_none()
            if question_to_update is not None:
                question_to_update.text = question.question
                await self.async_session.commit()
            return self.question_to_response(question_to_update)
        except Exception as e:
            print(f"Error: {e}")

    async def update_quiz(self, quiz:QuizResponse):
        try:
            quiz_to_update = await self.async_session.get(Quiz, quiz.id)
            quiz_to_update = quiz_to_update.scalar_one_or_none()
            if quiz_to_update:
                quiz_to_update.title = quiz.title
                quiz_to_update.description = quiz.description
                quiz_to_update.frequency = quiz.frequency
                return self.quiz_to_response(quiz_to_update)
        except Exception as e:
            print(f"Error: {e}")

    async def delete_quiz(self, quiz_id:int):
        try:
            quiz = await self.get_quiz(id=quiz_id)
            if not quiz:
                return DeleteScheme(
                    message="Quiz wasn't deleted",
                    id=-1
                )
            query = delete(Quiz).where(Quiz.id == quiz_id)
            result = await self.async_session.execute(query)
            await self.async_session.commit()
            if not result:
                return DeleteScheme(
                    message="Quiz wasn't deleted",
                    id=-1
                )
            logger.info(f"Quiz was deleted ID: {quiz_id}")
            return DeleteScheme(
                message="Quiz was successfully deleted",
                id=quiz_id)

        except Exception as e:
            print(f"An error occurred while deleting quiz: {e}")

    async def delete_question(self, question_id:int):
        try:
            question = await self.get_quiz(id=question_id)
            if not question:
                return DeleteScheme(
                    message="Question wasn't deleted",
                    id=-1
                )
            query = delete(Question).where(Question.id == question_id)
            result = await self.async_session.execute(query)
            await self.async_session.commit()
            if not result:
                return DeleteScheme(
                    message="Question wasn't deleted",
                    id=-1
                )
            logger.info(f"Question was deleted ID: {question_id}")
            return DeleteScheme(
                message="Question was successfully deleted",
                id=question_id)

        except Exception as e:
            print(f"An error occurred while deleting question: {e}")



    async def delete_option(self, option_id: int):
        try:
            option = await self.get_quiz(id=option_id)
            if not option:
                return DeleteScheme(
                    message="Option wasn't deleted",
                    id=-1
                )
            query = delete(Option).where(Option.id == option_id)
            result = await self.async_session.execute(query)
            await self.async_session.commit()
            if not result:
                return DeleteScheme(
                    message="Option wasn't deleted",
                    id=-1
                )
            logger.info(f"Option was deleted ID: {option_id}")
            return DeleteScheme(
                message="Option was successfully deleted",
                id=option_id)

        except Exception as e:
            print(f"An error occurred while deleting option: {e}")

    async def take_quiz(self, quiz_id: int, company_id:int, user_id:int, questions: QuestionsListScheme):
        quiz_result_rep = QuizResultRepository(database=self.async_session)
        total_questions = len(questions.questions)
        correct_answers = 0

        for question in questions.questions:
            query_option = select(Option).filter(and_(
                Option.is_correct == True,
                Option.question_id == question.id
            ))

            options = await self.async_session.execute(query_option)
            correct_option_ids = [option.id for option in options.scalars()]

            if question.option.id in correct_option_ids:
                correct_answers += 1

        total_questions, correct_answers = await quiz_result_rep.create_quiz_result(quiz_id, company_id, user_id,
                                                                                  correct_answers, total_questions)

        company_rating = await self.calculate_and_update_average_score_in_company(user_id=user_id, company_id=company_id)
        system_rating = await self.calculate_and_update_average_score_in_system(user_id=user_id)

        return company_rating, system_rating


    async def calculate_and_update_average_score_in_company(self, user_id: int, company_id: int) -> float:
        results = (
            self.async_session.query(QuizResult)
            .filter(QuizResult.user_id == user_id, QuizResult.company_id == company_id)
            .order_by(QuizResult.timestamp.asc())
            .all()
        )

        total_score = 0
        total_questions = 0

        for result in results:
            total_score += result.correct_answers
            total_questions += result.questions

        if total_questions == 0:
            return 0.0

        average_score = total_score / total_questions

        company_rating = CompanyRating(
            company_id=company_id,
            user_id=user_id,
            rating=average_score
        )
        self.async_session.add(company_rating)
        await self.async_session.commit()

        return average_score

    async def calculate_and_update_average_score_in_system(self, user_id: int) -> float:
        results = (
            self.async_session.query(QuizResult)
            .filter(QuizResult.user_id == user_id)
            .order_by(QuizResult.timestamp.asc())
            .all()
        )

        total_score = 0
        total_questions = 0

        for result in results:
            total_score += result.correct_answers
            total_questions += result.questions

        if total_questions == 0:
            return 0.0

        average_score = total_score / total_questions

        user = self.async_session.query(User).get(user_id)

        user.rating = average_score
        await self.async_session.commit()

        return average_score





