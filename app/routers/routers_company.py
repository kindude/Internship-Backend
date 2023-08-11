from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.company_repository import CompanyRepository
from schemas.Action import ActionResponse, ActionListResponse

from schemas.Company import CompanyResponse, CompanyScheme, CompanyDeleteScheme, CompanyListResponse, CompanySchemeRequest
from schemas.User import  UserResponse
from db.get_db import get_db

from utils.auth import get_current_user

router_companies = APIRouter()


@router_companies.post("/companies/create", response_model=CompanyResponse)
async def create_company(request: CompanySchemeRequest, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    request_ = CompanyScheme(
        name=request.name,
        description=request.description,
        site=request.site,
        city=request.city,
        country=request.country,
        is_visible=request.is_visible,
        owner_id=current_user.id
    )
    company = await company_repository.create_company(request_)
    if not company:
        raise HTTPException(status_code=404, detail="Something went wrong")

    return company


@router_companies.put("/companies/update/{id}", response_model=CompanyResponse)
async def update_company(id: int, request: CompanyScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    if current_user.id != request.owner_id:
        raise HTTPException(status_code=403, detail="You are not allowed to update company  profiles.")
    company_updated = await company_repository.update_company(id, request)
    return company_updated


@router_companies.post("/companies/{id}", response_model=CompanyDeleteScheme)
async def delete_company(id: int, request: CompanyScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> CompanyDeleteScheme:
    company_repository = CompanyRepository(database=db)
    print(current_user.id)
    if current_user.id != request.owner_id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete other companies ")
    company_deleted = await company_repository.delete_company(id)
    print(company_deleted)
    return company_deleted


@router_companies.get("/companies/all", response_model=CompanyListResponse)
async def get_all_companies(page: int = Query(1, alias="page"), per_page: int = Query(5), db: AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)) -> CompanyListResponse:
    company_repository = CompanyRepository(database=db)
    response = await company_repository.get_companies(page=page, per_page=per_page, current_user_id=current_user.id)
    return response


@router_companies.get("/companies/{id}", response_model=CompanyResponse)
async def get_company(id:int, db: AsyncSession = Depends(get_db)) -> CompanyResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router_companies.get("/companies/{id}/invites/all", response_model=ActionListResponse)
async def get_all_invitations(id: int, db: AsyncSession = Depends(get_db),
                              current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=id)
    if company.owner_id == current_user.id:
        invites = await company_repository.get_all_invites(company_id=company.id)
        if not invites:
            raise HTTPException(status_code=404, detail="You have not invites")
        return invites
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")

@router_companies.get("/companies/{id}/requests/all", response_model=ActionListResponse)
async def get_all_requests(id: int, db: AsyncSession = Depends(get_db),
                           current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=id)
    if company.owner_id == current_user.id:
        requests = await company_repository.get_all_requests(company_id=company.id)
        if not requests:
            raise HTTPException(status_code=404, detail="You have not requests")
        return requests
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")


@router_companies.get("/companies/{company_id}/users")
def get_users_in_company(company_id: int, db:AsyncSession = Depends(get_db), page: int = Query(1, alias="page"), per_page: int = Query(5)):
    company_repository = CompanyRepository(database=db)
    users_in_company = company_repository.get_users_in_company(company_id=company_id, page=page, per_page=per_page)
    if users_in_company:
        return users_in_company
    else:
        raise HTTPException(status_code=404, detail="No users in company found")
