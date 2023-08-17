import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db
from models.Models import Quiz

from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from repositories.quizzes_repository import QuizzRepository
from repositories.user_repository import UserRepository

from schemas.Action import ActionListResponse, ActionResponse, ActionScheme
from schemas.Company import CompanyListResponse
from schemas.Quiz import QuizResponse, QuizRequest
from schemas.User import UserResponse, UserResponseNoPass, UsersListResponse
from utils.auth import get_current_user

logger = logging.getLogger(__name__)
router_quiz = APIRouter()


@router_quiz.post("/company/create/quiz", response_model=QuizResponse, tags=["Quizzes"])
async def create_quiz(quiz: QuizRequest, db:AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=quiz.company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=quiz.company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            added_quiz = await quiz_repository.create_quizz(quiz)
            if added_quiz:
                return added_quiz
        else:
            raise HTTPException(status_code=403, detail="You are not allowed to create quizzes")


@router_quiz.post("/company/{company_id}/get-quiz/{quiz_id}", response_model=QuizResponse, tags=["Quizzes"])
async def get_quiz(company_id:int, quiz_id:int ,  db:AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            retrieved_quiz = await quiz_repository.get_quiz(id=quiz_id)
            return retrieved_quiz
        else:
            return None
