from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db
from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from repositories.quiz_result_repository import QuizResultRepository
from schemas.Company import ListCompanyUserLastCompletion
from schemas.Quiz import ListLastQuizCompletion
from schemas.QuizResult import UserQuizAveragesResponse
from schemas.User import UserResponse, ListUsersAverages
from utils.auth import get_current_user

router_quiz_result = APIRouter()


@router_quiz_result.get("/company/{company_id}/users/analytics", tags=["Analytics"], response_model=ListUsersAverages)
async def get_users_analytics(company_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repo = CompanyRepository(database=db)
    company = await company_repo.get_company(id=company_id)
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not an owner")
    quiz_res_repo = QuizResultRepository(database=db)
    return await quiz_res_repo.get_all_users_averages(company_id=company_id)


@router_quiz_result.get("/company/{company_id}/user/{user_id}/quizzes-averages", tags=["Analytics"], response_model=UserQuizAveragesResponse)
async def get_member_quizzes_averages(company_id: int, user_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repo = CompanyRepository(database=db)
    company = await company_repo.get_company(id=company_id)
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not an owner")
    quiz_res_repo = QuizResultRepository(database=db)
    return await quiz_res_repo.get_user_quiz_averages(user_id=user_id, company_id=company_id)


@router_quiz_result.get("/user/me/get-quizzes-averages", tags=["Analytics"], response_model=UserQuizAveragesResponse)
async def get_my_averages(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    quiz_res_repo = QuizResultRepository(database=db)
    return await quiz_res_repo.get_my_averages(user_id=current_user.id)


@router_quiz_result.get("/user/me/get-quizzes_and-times", tags=["Analytics"], response_model=ListLastQuizCompletion)
async def get_my_quizzes_time(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    quiz_res_repo = QuizResultRepository(database=db)
    return await quiz_res_repo.get_last_quiz_completion(user_id=current_user.id)


@router_quiz_result.get("/company/{company_id}/get-last-time", tags=["Analytics"], response_model=ListCompanyUserLastCompletion)
async def get_last_time_for_members(company_id:int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repo = CompanyRepository(database=db)
    company = await company_repo.get_company(id=company_id)
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not an owner")
    quiz_res_repo = QuizResultRepository(database=db)
    return await quiz_res_repo.get_company_users_last_completion(company_id=company_id)


