from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from schemas.Quiz import QuizScheme, QuestionScheme, OptionsListScheme, QuestionsListScheme


class QuizzRepository:
    def __init__(self, database: async_sessionmaker[AsyncSession]):
        self.async_session = database

    async def create_quizz(self, quiz: QuizScheme):
        pass

    async def create_questions(self, questions: QuestionsListScheme):
        pass

    async def create_options(self, options: OptionsListScheme):
        pass