from pydantic import EmailStr

from typing import List, Dict, Union
from pydantic import BaseModel

from typing import List, Union
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
    phone: str
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
    users: List[UserScheme]


class UserDetailsResponse(BaseModel):
    user: UserScheme


class UserDeleteScheme(BaseModel):
    message: str
    id: int


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    token:str