
from typing import List, Union, Optional
from pydantic import BaseModel, EmailStr


class UserScheme(BaseModel):
    username: str
    email: EmailStr
    password: str
    city: str
    country: str
    phone: str
    status: bool
    roles: List[str]


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    password: str
    city: str
    country: str
    phone: Optional[str]
    status: bool
    roles: List[str]

class UserResponseNoPass(BaseModel):
    id: int
    username: str
    email: str
    city: str
    country: str
    phone: Optional[str]
    status: bool
    roles: List[str]


class UserToken(BaseModel):
    username:str
    email:str
class SignIn(BaseModel):
    email: EmailStr
    password: str


class SignUp(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    username: str
    email: EmailStr


class UsersListResponse(BaseModel):
    users: List[UserResponse]
    per_page: int
    page: int
    total: int
    total_pages: int


class UserDetailsResponse(BaseModel):
    user: UserScheme


class UserDeleteScheme(BaseModel):
    message: str
    id: int


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    token: str


class UsersAverage(BaseModel):
    user_id: str
    average: float
    time: str


class ListUsersAverages(BaseModel):
    averages: List[UsersAverage]


class MyAverages(BaseModel):
    quiz_id: int
    average: str
    timestamp: str
    total_questions: int
    total_correct_answers: int
