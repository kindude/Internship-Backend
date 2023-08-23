from typing import List

from pydantic import BaseModel

from schemas.Question import QuestionAddRequest, QuestionResponse


class QuizAddRequest(BaseModel):
    title: str
    description: str
    frequency: int
    company_id: int
    questions: List[QuestionAddRequest]


class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    frequency: int
    company_id: int


class QuizListResponse(BaseModel):
    quizzes: List[QuizResponse]


class QuizUpdateScheme(BaseModel):
    id: int
    title: str
    description: str
    frequency: int


class DeleteScheme(BaseModel):
    message: str
    id: int

