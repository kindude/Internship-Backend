from datetime import datetime
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
    per_page: int
    page: int
    total: int
    total_pages: int


class CompanyDeleteScheme(BaseModel):
    message: str
    id: int

class CompanyUserLastCompletion(BaseModel):
    user_id: int
    last_completion_time: datetime

class ListCompanyUserLastCompletion(BaseModel):
    last_completions: List[CompanyUserLastCompletion]