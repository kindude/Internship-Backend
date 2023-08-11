import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db

from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository

from schemas.Action import ActionListResponse, ActionResponse
from schemas.User import UserResponse
from utils.auth import get_current_user

logger = logging.getLogger(__name__)
router_action = APIRouter()


@router_action.post("/users/request/create", response_model=ActionResponse)
async def create_invite(request: ActionResponse, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> ActionResponse:
    action_repository = ActionRepository(database=db)
    if current_user.id == request.user_id:
        new_request = await action_repository.create_request(request_=request)
        return new_request
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to create invites")


@router_action.get("/users/invites/all", response_model=ActionListResponse)
async def get_all_invitations(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
        action_repository = ActionRepository(database=db)
        invites = await action_repository.get_all_invites(current_user.id)
        if not invites:
            raise HTTPException(status_code=404, detail="You have not invites")
        return invites


@router_action.get("/users/requests/all", response_model=ActionListResponse)
async def get_all_requests(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    action_repository = ActionRepository(database=db)
    requests = await action_repository.get_all_requests(current_user.id)
    if not requests:
        raise HTTPException(status_code=404, detail="You have not requests")
    return requests


@router_action.get("/companies/{id}/invites/all", response_model=ActionListResponse)
async def get_all_invitations(id: int, db: AsyncSession = Depends(get_db),
                              current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=id)
    action_repository = ActionRepository(database=db)

    if company.owner_id == current_user.id:
        invites = await action_repository.get_all_invites(company_id=id)
        if not invites:
            raise HTTPException(status_code=404, detail="You have not invites")
        return invites
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")

@router_action.get("/companies/{id}/requests/all", response_model=ActionListResponse)
async def get_all_requests(id: int, db: AsyncSession = Depends(get_db),
                           current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=id)
    action_repository = ActionRepository(database=db)
    if company.owner_id == current_user.id:
        requests = await action_repository.get_all_requests(company_id=id)
        if not requests:
            raise HTTPException(status_code=404, detail="You have not requests")
        return requests
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")


@router_action.get("/companies/{company_id}/users")
def get_users_in_company(company_id: int, db:AsyncSession = Depends(get_db), page: int = Query(1, alias="page"), per_page: int = Query(5)):
    action_repository = ActionRepository(database=db)
    users_in_company = action_repository.get_users_in_company(company_id=company_id, page=page, per_page=per_page)
    if users_in_company:
        return users_in_company
    else:
        raise HTTPException(status_code=404, detail="No users in company found")