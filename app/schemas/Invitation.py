from typing import List, Union
from pydantic import BaseModel, EmailStr


class InvitationResponse(BaseModel):
    id: int
    user_id: int
    company_id: int
    status: str

class InvitationReponseList(BaseModel):
    invites: List[InvitationResponse]