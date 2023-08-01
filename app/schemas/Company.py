from typing import List, Union
from pydantic import BaseModel, EmailStr

from schemas.User import UserScheme


class CompanyScheme(BaseModel):
    name: str
    description: str
    site: str
    city: str
    country: str
    owner_id: int


class CompanyResponse(BaseModel):
    id: id
    name: str
    description: str
    site: str
    city: str
    country: str
    owner_id: int


class CompanyListResponse(BaseModel):
    users: List[CompanyScheme]

