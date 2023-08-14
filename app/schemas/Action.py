from typing import List, Union
from pydantic import BaseModel, EmailStr


class ActionResponse(BaseModel):
    user_id: int
    company_id: int
    status: str
    type_of_action: str


class ActionScheme(ActionResponse):
    id:int
class ActionListResponse(BaseModel):
    actions: List[ActionResponse]