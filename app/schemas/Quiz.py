from typing import List

from pydantic import BaseModel


class OptionScheme(BaseModel):
    id:int
    text:str
    question_id:int
    is_correct:bool


class OptionsListScheme(BaseModel):
    options: List[OptionScheme]


class QuestionScheme(BaseModel):
    id:int
    question: str
    quiz_id:int
    options: List[OptionScheme]


class QuestionsListScheme(BaseModel):
    questions: List[QuestionScheme]


class QuizResponse(BaseModel):
    title:str
    description:str
    frequency:str
    company_id:int
    questions: List[QuestionScheme]
class QuizScheme(QuizResponse):
    id:int



