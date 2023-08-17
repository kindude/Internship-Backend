from typing import List

from pydantic import BaseModel


class OptionResponse(BaseModel):
    text:str
    question_id:int
    is_correct:bool

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
    options: List[OptionResponse]


class QuestionsListScheme(BaseModel):
    questions: List[QuestionResponse]


class QuizResponse(BaseModel):
    title: str
    description: str
    frequency: int
    company_id: int
    questions: List[QuestionResponse]


class QuizRequest(QuizResponse):
    questions: List[QuestionRequest]
class QuizScheme(QuizResponse):
    id:int



