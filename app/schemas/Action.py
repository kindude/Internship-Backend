from typing import List, Union
from pydantic import BaseModel, EmailStr


class ActionResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    status: str
    type:str


class ActionListResponse(BaseModel):
    actions: List[ActionResponse]