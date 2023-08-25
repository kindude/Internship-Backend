from datetime import datetime

from pydantic import BaseModel


class QuizResultAddRequest(BaseModel):
    company_id: int
    user_id: int
    quiz_id: int
    correct_answers: int
    questions: int
    timestamp: datetime