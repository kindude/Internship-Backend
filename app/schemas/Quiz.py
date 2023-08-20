from typing import List

from pydantic import BaseModel


class OptionResponse(BaseModel):
    text: str
    question_id: int


class OptionRequest(BaseModel):
    text:str
    is_correct:bool

class OptionScheme(OptionResponse):
    id:int



class OptionsListScheme(BaseModel):
    options: List[OptionResponse]


class QuestionResponse(BaseModel):
    question: str
    quiz_id:int
    options: List[OptionResponse]

class QuestionRequest(BaseModel):
    question: str
    options: List[OptionRequest]


class QuestionScheme(QuestionResponse):
    id: int
    question: str
    quiz_id: int
    options: List[OptionScheme]


class QuestionsListScheme(BaseModel):
    questions: List[QuestionScheme]


class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    frequency: int
    company_id: int


class QuestionListRequest(QuestionResponse):
    questions: List[QuestionResponse]


class QuizRequest(BaseModel):
    title: str
    description: str
    frequency: int
    company_id: int

class QuizScheme(QuizResponse):
    id:int
class QuizListResponse(BaseModel):
    quizzes: List[QuizResponse]


class DeleteScheme(BaseModel):
    message: str
    id: int

