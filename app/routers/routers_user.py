from fastapi import HTTPException

from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from repositories.user_repository import UserRepository
from schemas.Action import ActionListResponse
from schemas.Company import CompanyResponse, CompanyScheme
from schemas.User import UserScheme, UserResponse, UsersListResponse, UserDeleteScheme, UserLogin, UserResponseNoPass
from db.get_db import get_db

from utils.auth import get_current_user
router_user = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router_user.post("/users/register", response_model=UserResponse)
async def create_user(request: UserScheme, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    exists = await user_repository.get_user_by_email(email=request.email)
    if exists is None:
        user = await user_repository.create_user(request=request)
        user = await user_repository.get_user_by_email(email=request.email)
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
    else:
        return exists


@router_user.put("/users/update/{id}", response_model=UserResponseNoPass)
async def update_user(id: int, request: UserScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> UserResponseNoPass:
    user_repository = UserRepository(database=db)
    current_user_profile = await user_repository.get_user_by_email(email=current_user.email)
    if current_user_profile.id != id:
        raise HTTPException(status_code=403, detail="You are not allowed to update this user profiles.")

    updated_user = await user_repository.update_user(id=id, request=request)
    return UserResponseNoPass(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        city=updated_user.city,
        country=updated_user.country,
        phone=updated_user.phone,
        status=updated_user.status,
        roles=updated_user.roles,
    )

@router_user.delete("/users/{id}", response_model=UserDeleteScheme)
async def delete_user(id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> UserDeleteScheme:
    user_repository = UserRepository(database=db)
    if current_user.id != id:
        print(current_user.id)
        print(id)
        raise HTTPException(status_code=403, detail="You are not allowed to delete other users' profiles.")

    res = await user_repository.del_user(id=id)
    return res


@router_user.get("/users/all", response_model=UsersListResponse)
async def get_all(page: int = Query(1, alias="page"), per_page: int = Query(10), db: AsyncSession = Depends(get_db)) -> UsersListResponse:
    user_repository = UserRepository(database=db)
    response = await user_repository.get_users(page=page, per_page=per_page)
    return response


@router_user.get("/users/{id}", response_model=UserResponseNoPass)
async def get_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponseNoPass:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user(id=id)
    if not query:
        raise HTTPException(status_code=404, detail="User not found")
    return query


@router_user.post("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user


@router_user.get("/users/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user_by_username(username=username)
    return query


@router_user.post("/users/login", response_model=str)
async def user_login(request: UserLogin, db: AsyncSession = Depends(get_db)) -> str:
    user_repository = UserRepository(database=db)
    print(request)
    token = await user_repository.authenticate_user(request=request)
    return token.token









