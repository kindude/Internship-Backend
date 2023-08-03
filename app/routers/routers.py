from http.client import HTTPException

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.company_repository import CompanyRepository
from repositories.user_repository import UserRepository
from schemas.Company import CompanyResponse, CompanyScheme, CompanyDeleteScheme, CompanyListResponse
from schemas.User import UserScheme, UserResponse, UsersListResponse, UserDeleteScheme, UserLogin, Token
from db.get_db import get_db
from services.create_user_scheme import user_scheme_raw_from_data
from utils.auth import get_user_email_by_token
from utils.auth import get_current_user
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.post("/users/register", response_model=UserResponse)
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


@router.post("/users/update/{id}", response_model=UserResponse)
async def update_user(id: int, request: UserScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    user_repository = UserRepository(database=db)
    current_user_profile = await user_repository.get_user_by_email(email=current_user.email)
    if current_user_profile.id != id:
        raise HTTPException(status_code=403, detail="You are not allowed to update other users' profiles.")

    updated_user = await user_repository.update_user(id=id, request=request)
    return updated_user


@router.delete("/users/{id}", response_model=UserDeleteScheme)
async def delete_user(id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> UserDeleteScheme:
    user_repository = UserRepository(database=db)
    current_user_profile = await user_repository.get_user_by_email(email=current_user.email)

    if current_user_profile.id != id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete other users' profiles.")

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


@router.post("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user


@router.get("/users/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user_by_username(username=username)
    return query


@router.post("/users/login", response_model=str)
async def user_login(request: UserLogin, db: AsyncSession = Depends(get_db)) -> str:
    user_repository = UserRepository(database=db)
    token = await user_repository.authenticate_user(request=request)
    return token.token


@router.post("/companies/update/{id}", response_model=CompanyResponse)
async def update_company(id: int, request: CompanyScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    if current_user.id != request.owner_id:
        raise HTTPException(status_code=403, detail="You are not allowed to update other users' profiles.")
    company_updated = await company_repository.update_company(id, request)
    return company_updated


@router.delete("/companies/{id}", response_model=CompanyDeleteScheme)
async def delete_company(id: int, request: CompanyScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> CompanyDeleteScheme:
    company_repository = CompanyRepository(database=db)
    if current_user.id != request.owner_id:
        raise HTTPException(status_code=403, detail="You are not allowed to update other users' profiles.")
    company_deleted = await company_repository.delete_company(id)
    return company_deleted


@router.get("/companies/all", response_model=CompanyListResponse)
async def get_all(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)) -> CompanyListResponse:
    company_repository = CompanyRepository(database=db)
    response = await company_repository.get_companies(page=page, per_page=per_page)
    return response


@router.get("/companies/{id}", response_model=CompanyResponse)
async def get_company(id:int, db:AsyncSession = Depends(get_db)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id)
    return company


@router.post("/companies/{id}/visibility", response_model=CompanyResponse)
async def set_visibility(id:int, request: str, db: AsyncSession = Depends(get_db)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.change_visibility(id, request)
    return company
