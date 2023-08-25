from typing import List

from pydantic import BaseModel

from schemas.Option import OptionAddRequest, OptionResponse


class QuestionAddRequest(BaseModel):
    question: str
    options: List[OptionAddRequest]


class QuestionResponse(BaseModel):
    id: int
    text: str
    quiz_id: int
    options: List[OptionResponse]


class QuestionTakeQuiz(BaseModel):
    id: int
    text: str
    quiz_id: int
    option: OptionResponse



class QuestionUpdateScheme(BaseModel):
    id: int
    text: str


class QuestionListResponse(BaseModel):
    questions: List[QuestionResponse]
