import os
from http.client import HTTPException

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository
from schemas.User import UserScheme, UserResponse, UsersListResponse, UserDeleteScheme, UserLogin, Token
from db.get_db import get_db
from utils.auth import get_user_by_token

router = APIRouter()



@router.post("/create", response_model=UserResponse)
async def create_user(request: UserScheme, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    user = await user_repository.create_user(request=request)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        password=user.password,
        city=user.city,
        country=user.country,
        phone=user.phone,
        status=user.status,
        roles=user.roles,
    )



@router.post("/updateUser/{id}", response_model=UserResponse)
async def update_user(id:int, request: UserScheme, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    updated_user = await user_repository.update_user(id=id, request=request)
    return updated_user


@router.delete("/{id}", response_model=UserDeleteScheme)
async def delete_user(id: int, db: AsyncSession = Depends(get_db)) -> UserDeleteScheme:
    user_repository = UserRepository(database=db)
    res = await user_repository.del_user(id=id)
    return res

@router.get("/all")
async def get_all(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)) -> UsersListResponse:
    user_repository = UserRepository(database=db)
    response = await user_repository.get_users(page=page, per_page=per_page)
    return response


@router.get("/{id}", response_model=UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user(id=id)
    return query


@router.post("/me", response_model=UserScheme)
async def get_current_user(request: Token) -> UserScheme:

    user = await get_user_by_token(request=request)
    return user


@router.get("/username/{username}", response_model=UserScheme)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> UserScheme:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user_by_username(username=username)
    return query


@router.post("/login", response_model=str)
async def user_login(request: UserLogin, db: AsyncSession = Depends(get_db))->str:
    user_repository = UserRepository(database=db)
    res = await user_repository.authenticate_user(request=request)
    return res

# @router.get("/secure")
# async def secure_route(token: str = Depends(get_user_by_token)):
#     return {"message": "Доступ разрешен", "user":"1"}


AUTH0_DOMAIN = "dev-nusd43iygpsjwqlj.us.auth0.com"
API_AUDIENCE = "https://auth-reg"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:

    payload = jwt.decode(token, os.getenv("AUTH0_SECRET_KEY"), algorithms=[ALGORITHM], audience=API_AUDIENCE)
    print("Payload:", payload)  # Add this line to print the payload
    return payload



@router.post("/api/secure")
async def secure_route(current_user: dict = Depends(get_current_user)):
    return {"message": "Доступ разрешен", "user": current_user}


