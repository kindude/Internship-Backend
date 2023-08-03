from http.client import HTTPException

from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.company_repository import CompanyRepository

from schemas.Company import CompanyResponse, CompanyScheme, CompanyDeleteScheme, CompanyListResponse
from schemas.User import  UserResponse
from db.get_db import get_db

from utils.auth import get_current_user



router_companies = APIRouter()

@router_companies.delete("/companies/{id}", response_model=CompanyDeleteScheme)
async def delete_company(id: int, request: CompanyScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> CompanyDeleteScheme:
    company_repository = CompanyRepository(database=db)
    if current_user.id != request.owner_id:
        raise HTTPException(status_code=403, detail="You are not allowed to update other users' profiles.")
    company_deleted = await company_repository.delete_company(id)
    return company_deleted


@router_companies.get("/companies/all", response_model=CompanyListResponse)
async def get_all(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)) -> CompanyListResponse:
    company_repository = CompanyRepository(database=db)
    response = await company_repository.get_companies(page=page, per_page=per_page)
    return response


@router_companies.get("/companies/{id}", response_model=CompanyResponse)
async def get_company(id:int, db:AsyncSession = Depends(get_db)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id)
    return company


@router_companies.post("/companies/{id}/visibility", response_model=CompanyResponse)
async def set_visibility(id:int, request: str, db: AsyncSession = Depends(get_db)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.change_visibility(id, request)
    return company