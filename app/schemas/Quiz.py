from typing import List

from pydantic import BaseModel

from schemas.Question import QuestionAddRequest, QuestionResponse, QuestionUpdateScheme


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
    questions: List[QuestionUpdateScheme]


class DeleteScheme(BaseModel):
    message: str
    id: int


class LastQuizCompletion(BaseModel):
    quiz_id: int
    last_completion_time: str


class ListLastQuizCompletion(BaseModel):
    completions: List[LastQuizCompletion]
