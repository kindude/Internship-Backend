from pydantic import EmailStr

from typing import List, Dict, Union
from pydantic import BaseModel

from typing import List, Union
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    username: str
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
    users: List[Dict[str, Union[int, str]]]


class UserDetailsResponse(BaseModel):
    user: User
