import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db

from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from repositories.user_repository import UserRepository

from schemas.Action import ActionListResponse, ActionResponse, ActionScheme
from schemas.Company import CompanyListResponse
from schemas.User import UserResponse, UserResponseNoPass, UsersListResponse
from utils.auth import get_current_user

logger = logging.getLogger(__name__)
router_action = APIRouter()


######################User########################################
@router_action.post("/action/request/create", response_model=ActionResponse, tags=["Actions_users"])
async def create_request(request: ActionResponse, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> ActionResponse:
    action_repository = ActionRepository(database=db)
    if current_user.id == request.user_id:
        new_request = await action_repository.create_request(request_=request)
        return new_request
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to create invites")


@router_action.get("/action/invites/all", response_model=ActionListResponse, tags=["Actions_users"])
async def get_all_invitations(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    action_repository = ActionRepository(database=db)
    if current_user:
        invites = await action_repository.get_all_invites_user(current_user.id)
        if not invites:
            raise HTTPException(status_code=404, detail="You have not invites")
        return invites


@router_action.get("/action/requests/all", response_model=ActionListResponse, tags=["Actions_users"])
async def get_all_requests(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    action_repository = ActionRepository(database=db)
    requests = await action_repository.get_all_requests_user(current_user.id)
    if not requests:
        raise HTTPException(status_code=404, detail="You have not requests")
    return requests

@router_action.post("/action/invite/reject", tags=["Actions_users"])
async def reject_invite(request: ActionScheme, db:AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    if request.user_id == current_user.id:
        invite = await action_repository.reject_invite(request)
        if not invite:
            raise HTTPException(status_code=404, detail="An error occurred while rejecting the invite")
        return invite
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to reject any invites")


@router_action.post("/action/invite/accept", tags=["Actions_users"])
async def accept_invite(request: ActionScheme, db:AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    if request.user_id == current_user.id:
        invite = await action_repository.accept_invite(request)
        if not invite:
            raise HTTPException(status_code=404, detail="An error occurred while accepting the invite")
        return invite
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to accept any invites")

@router_action.post("/action/request/cancel", tags=["Actions_users"])
async def cancel_request(request: ActionScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(request.company_id)
    if request.user_id == current_user.id:
        cancelled_request = await action_repository.cancel_request(request)
        if not cancelled_request:
            raise HTTPException(status_code=404, detail="An error occurred while cancelling  the request")
        return cancelled_request
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to cancel any requests")

@router_action.post("/action/leave_company/{company_id}", tags=["Actions_users"])
async def leave_company(company_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    if company.owner_id == current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to leave your own company")
    result = await action_repository.leave_company(company_id=company_id, user_id=current_user.id)
    return result


######################Company########################################
@router_action.post("/companies/invite/create", tags=["Actions_company"])
async def create_invite(request: ActionResponse, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(request.company_id)
    if request.user_id != current_user.id:
        if company.owner_id == current_user.id:
            action_repository = ActionRepository(database=db)
            invite = await action_repository.create_invite(request)
            if not invite:
                raise HTTPException(status_code=404, detail="Not found invite")
        else:
            raise HTTPException(status_code=404, detail="You are not allowed to create invites")
        return invite
    else:
        raise HTTPException(status_code=403, detail="You cannot send invites from your own company")


@router_action.post("/action/invite/cancel", tags=["Actions_users"])
async def cancel_invite(request: ActionScheme, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(request.company_id)
    if company.owner_id == current_user.id:
        cancelled_request = await action_repository.cancel_request(request)
        if not cancelled_request:
            raise HTTPException(status_code=404, detail="An error occurred while cancelling  the request")
        return cancelled_request
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to cancel any requests")

@router_action.get("/companies/{id}/invites/all", response_model=ActionListResponse, tags=["Actions_company"])
async def get_all_invitations(id: int, db: AsyncSession = Depends(get_db),
                              current_user: UserResponse = Depends(get_current_user)) -> ActionListResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=id)
    action_repository = ActionRepository(database=db)

    if company.owner_id == current_user.id:
        invites = await action_repository.get_all_invites_company(company_id=id)
        if not invites:
            raise HTTPException(status_code=404, detail="You have not invites")
        return invites
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")

@router_action.get("/companies/{id}/requests/all", response_model=ActionListResponse, tags=["Actions_company"])
async def get_all_requests(id: int, db: AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)) -> ActionListResponse:
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=id)
    action_repository = ActionRepository(database=db)
    if company.owner_id == current_user.id:
        requests = await action_repository.get_all_requests_company(company_id=id)
        if not requests:
            raise HTTPException(status_code=404, detail="You have not requests")
        return requests
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")

@router_action.post("/companies/{company_id}/request/accept", tags=["Actions_company"])
async def accept_request(company_id:int, request:ActionScheme, current_user:UserResponse = Depends(get_current_user), db:AsyncSession = Depends(get_db)):
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(company_id)
    if company.owner_id == current_user.id:
        accepted_request = await action_repository.accept_request(request)
        return accepted_request
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")

@router_action.post("/companies/{company_id}/request/reject", tags=["Actions_company"])
async def reject_request(company_id: int, request: ActionScheme,
                         current_user: UserResponse = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(company_id)
    if company.owner_id == current_user.id:
        rejected_request = await action_repository.reject_request(request)
        return rejected_request
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")


@router_action.post("/companies/{company_id}/remove_user/{user_id}", tags=["Actions_company"])
async def remove_user_from_company(company_id: int, user_id:int,
                         current_user: UserResponse = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):

    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)

    if user_id == current_user.id:
        raise HTTPException(status_code=403, detail="You are not allowed to remove yourself")
    company = await company_repository.get_company(id=company_id)
    if company.owner_id == current_user.id:
        result = await action_repository.remove_user_from_company(user_id=user_id, company_id=company_id)
        return result
    else:
        raise HTTPException(status_code=403, detail="You can't interact with this company")


@router_action.get("/companies/{company_id}/members", tags=["Actions_company"])
async def get_users_in_company(company_id: int, db: AsyncSession = Depends(get_db), page: int = Query(1, alias="page"), per_page: int = Query(5)):
    action_repository = ActionRepository(database=db)
    users_in_company = await action_repository.get_users_in_company(company_id=company_id, page=page, per_page=per_page)
    if users_in_company:
        return users_in_company
    else:
        raise HTTPException(status_code=404, detail="No users in company found")


@router_action.get("/companies/user/in", tags=["Actions_company"], response_model=CompanyListResponse)
async def get_users_in_company(db: AsyncSession = Depends(get_db), page: int = Query(1, alias="page"), per_page: int = Query(5), current_user: UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    companies_im_in = await action_repository.get_all_companies_im_in(current_user_id=current_user.id, page=page, per_page=per_page)
    if companies_im_in:
        return companies_im_in
    else:
        raise HTTPException(status_code=404, detail="No companies found")


@router_action.put("/companies/{company_id}/add_admin/{user_id}", response_model=UserResponseNoPass, tags=["Admin"])
async def toggle_admin_role(company_id:int, user_id:int, current_user: UserResponse = Depends(get_current_user), db:AsyncSession = Depends(get_db)) -> UserResponseNoPass:
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    if company.owner_id == current_user.id:
        user_admin = await action_repository.add_admin(user_id=user_id, company_id=company_id)
        if not user_admin:
            raise HTTPException(status_code=404, detail="Something went wrong during adding an admin")
        return user_admin
    else:
        raise HTTPException(status_code=403, detail="You cannot assign admins for this company")


@router_action.put("/companies/{company_id}/remove_admin/{user_id}", response_model=UserResponseNoPass, tags=["Admin"])
async def remove_admin_role(company_id:int, user_id:int, current_user: UserResponse = Depends(get_current_user), db:AsyncSession = Depends(get_db)) -> UserResponseNoPass:
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    if company.owner_id == current_user.id:
        user_admin = await action_repository.remove_admin(id=user_id)
        if not user_admin:
            raise HTTPException(status_code=404, detail="Something went wrong during removing an admin")
        return user_admin
    else:
        raise HTTPException(status_code=403, detail="You cannot remove admins for this company")


@router_action.get("/companies/{company_id}/admins/all", response_model=UsersListResponse, tags=["Admin"])
async def get_all_admins(company_id:int, current_user:UserResponse=Depends(get_current_user), db:AsyncSession = Depends(get_db),
                         page: int = Query(1, alias="page"), per_page: int = Query(10)) -> UsersListResponse:
    action_repository = ActionRepository(database=db)
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    if company.owner_id == current_user.id:
        admins = await action_repository.get_all_admins(company_id=company_id,per_page=per_page, page=page)
        if not admins:
            raise HTTPException(status_code=404, detail="Admins for this company not found")
        return admins
    else:
        raise HTTPException(status_code=403, detail="You are not allowed to interact with this company")


