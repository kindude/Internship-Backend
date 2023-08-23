from typing import List

from pydantic import BaseModel


class OptionAddRequest(BaseModel):
    text: str
    is_correct: bool


class OptionResponse(BaseModel):
    id: int
    text: str


class OptionUpdateScheme(BaseModel):
    id: int
    text: str
    is_correct: bool

class OptionListResponse(BaseModel):
    options: List[OptionResponse]





