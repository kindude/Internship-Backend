from typing import List, Union
from pydantic import BaseModel, EmailStr

from schemas.User import UserScheme


class CompanySchemeRequest(BaseModel):
    name: str
    description: str
    site: str
    city: str
    country: str
    is_visible: bool


class CompanyScheme(CompanySchemeRequest):
    owner_id: int


class CompanyResponse(CompanyScheme):
    id: int


class CompanyListResponse(BaseModel):
    companies: List[CompanyResponse]


class CompanyDeleteScheme(BaseModel):
    message: str
    id: int