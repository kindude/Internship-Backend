from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    email: EmailStr
    username: str


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
    users: list[User]


class UserDetailsResponse(BaseModel):
    user: User
