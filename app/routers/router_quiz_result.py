from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db
from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from repositories.quiz_result_repository import QuizResultRepository
from schemas.User import UserResponse
from utils.auth import get_current_user

router_quiz_result = APIRouter()


@router_quiz_result.get("company/{company_id}/user/{user_id}/analytics")
async def get_user_avg(company_id: int, user_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    action_repo = ActionRepository(database=db)
    company_repo = CompanyRepository(database=db)
    quiz_res_repo = QuizResultRepository(database=db)
    company = await company_repo.get_company(id=company_id)
    if current_user.id != user_id:
        users = await action_repo.get_users_in_company(company_id=company_id)
        user_ids = [user.id for user in users.users]
        if company.owner_id == current_user.id and user_id in user_ids:
            return quiz_res_repo.get_user_quiz_averages(user_id=user_id)

        raise HTTPException(status_code=403, detail="You are not allowed")


@router_quiz_result.get("company/{company_id}/quizzes/averages")
async def get_quiz_avg(company_id: int, quiz_id: int, db: AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)):
    company_repo = CompanyRepository(database=db)
    company = await company_repo.get_company(id=company_id)
    if current_user.id != company.owner_id:
        raise HTTPException(status_code=403, detail="You are not an owner of the company")
    quiz_res_repo = QuizResultRepository(database=db)
    await quiz_res_repo.get_quiz_averages()


@router_quiz_result.get("/company/{company_id}/users/analytics", tags=["Analytics"])
async def get_users_analytics(company_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repo = CompanyRepository(database=db)
    company = await company_repo.get_company(id=company_id)
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not an owner")
    quiz_res_repo = QuizResultRepository(database=db)
    return await quiz_res_repo.get_all_users_averages(company_id=company_id)







