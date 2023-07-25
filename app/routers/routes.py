
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.User import User
from repositories.user_repository import UserRepository
from schemas.User import UserScheme, UserResponse, UsersListResponse, UserDeleteScheme, UserLogin, Token
from db.get_db import get_db
from utils.auth import get_user_email_by_token
from utils.auth import get_current_user
router = APIRouter()



@router.post("/users/create", response_model=UserResponse)
async def create_user(request: UserScheme, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    user = await user_repository.create_user(request=request)

    return user


@router.post("/users/update/{id}", response_model=UserResponse)
async def update_user(id:int, request: UserScheme, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    updated_user = await user_repository.update_user(id=id, request=request)
    return updated_user


@router.delete("/users/{id}", response_model=UserDeleteScheme)
async def delete_user(id: int, db: AsyncSession = Depends(get_db)) -> UserDeleteScheme:
    user_repository = UserRepository(database=db)
    res = await user_repository.del_user(id=id)
    return res


@router.get("/users/all", response_model=UsersListResponse)
async def get_all(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)) -> UsersListResponse:
    user_repository = UserRepository(database=db)
    response = await user_repository.get_users(page=page, per_page=per_page)
    return response


@router.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user(id=id)
    return query


@router.post("/users/me", response_model=UserResponse)
async def get_me(request: Token, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    email = get_user_email_by_token(request=request)
    user = await user_repository.get_user_by_email(email=email)
    return user


@router.get("/users/{username}", response_model=UserScheme)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> UserScheme:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user_by_username(username=username)
    return query


@router.post("/users/login", response_model=Token)
async def user_login(request: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    user_repository = UserRepository(database=db)
    token = await user_repository.authenticate_user(request=request)
    return token


@router.post("/create_user_from_auth0/")
async def create_user_from_auth0(access_token: str, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    user_email = get_current_user(token=access_token)
    user = await user_repository.get_user_by_email(user_email)
    if not user:
        user = UserScheme(email=user_email, username=user_email,
                          password=user_repository.create_password(),
                          city="None",
                          country="None",
                          phone=13*"0",
                          status=True,
                          roles=["user"]
                          )
        created_user = await user_repository.create_user(user)
        return created_user
    else:
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



