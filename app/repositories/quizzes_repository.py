from typing import List

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy import select, delete, desc
from sqlalchemy.orm import selectinload

from models.Models import Quiz, Question, Option
from schemas.Quiz import QuizScheme, QuestionScheme, OptionsListScheme, QuestionsListScheme, QuizResponse, \
    QuestionResponse, OptionResponse, QuizRequest


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