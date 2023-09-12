from datetime import datetime
from typing import List, Dict

from pydantic import BaseModel


class QuizResultAddRequest(BaseModel):
    company_id: int
    user_id: int
    quiz_id: int
    correct_answers: int
    questions: int
    timestamp: datetime


class Average(BaseModel):
    quiz_id: int
    average: str
    timestamp: str
    total_questions: int
    total_correct_answers: int

class QuizAverage(BaseModel):
    Avges: Dict[int, Average]

class UserQuizAveragesResponse(BaseModel):
    averages: List[QuizAverage]