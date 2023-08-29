import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.get_db import get_db

from repositories.action_repository import ActionRepository
from repositories.company_repository import CompanyRepository
from repositories.quiz_result_repository import QuizResultRepository
from repositories.quizzes_repository import QuizzRepository
from schemas.Option import OptionUpdateScheme, OptionResponse
from schemas.Question import QuestionListResponse, QuestionUpdateScheme, QuestionTakeQuiz

from schemas.Quiz import QuizResponse, QuizListResponse, QuestionResponse, QuizAddRequest, QuizUpdateScheme, \
    DeleteScheme

from schemas.User import UserResponse
from utils.auth import get_current_user

logger = logging.getLogger(__name__)
router_quiz = APIRouter()


@router_quiz.post("/company/create/quiz", response_model=QuizResponse, tags=["Quizzes"])
async def create_quiz(quiz: QuizAddRequest, db:AsyncSession = Depends(get_db), current_user:UserResponse = Depends(get_current_user)):
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


@router_quiz.get("/company/{company_id}/get-quiz/{quiz_id}", response_model=QuizResponse, tags=["Quizzes"])
async def get_quiz(company_id:int, quiz_id:int ,  db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    member = await action_repository.if_member(user_id=current_user.id, company_id=company_id)
    if member:
        quiz_repository = QuizzRepository(database=db)
        retrieved_quiz = await quiz_repository.get_quiz(id=quiz_id)
        return retrieved_quiz
    raise HTTPException(status_code=403, detail="You are not a member of the company")


@router_quiz.get("/company/{company_id}/get-quizzes/", response_model=QuizListResponse, tags=["Quizzes"])
async def get_quizzes(company_id: int,  db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    quiz_repository = QuizzRepository(database=db)
    if action_repository.if_member(user_id=current_user.id, company_id=company_id):
        retrieved_quizzes = await quiz_repository.get_quizzes(company_id=company_id)
        if retrieved_quizzes:
            return retrieved_quizzes
    raise HTTPException(status_code=404, detail="None quizzes")

@router_quiz.get("/company/{company_id}/quiz/{quiz_id}/questions", response_model=QuestionListResponse, tags=["Quizzes"])
async def get_questions(company_id: int, quiz_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    action_repository = ActionRepository(database=db)
    quiz_repository = QuizzRepository(database=db)
    if action_repository.if_member(user_id=current_user.id, company_id=company_id):
        questions = await quiz_repository.get_questions(quiz_id=quiz_id)
        if questions:
            return questions
        raise HTTPException(status_code=404, detail="None questions for this quiz")


@router_quiz.post("/company/{company_id}/quiz/update", response_model=QuizResponse, tags=["Quizzes"])
async def update_quiz(company_id: int, quiz:QuizUpdateScheme, db:AsyncSession = Depends(get_db), current_user:UserResponse =Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            updated_quiz = await quiz_repository.update_quiz(quiz=quiz)
            return updated_quiz
        raise HTTPException(status_code=403, detail="You are not allowed to update quizzes")


@router_quiz.post("/company/{company_id}/quiz/question/update", response_model=QuestionResponse, tags=["Quizzes"])
async def update_question(company_id: int, question: QuestionUpdateScheme,
                          db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            updated_question = await quiz_repository.update_question(question=question)
            return updated_question
        raise HTTPException(status_code=403, detail="You are not allowed to update questions")


@router_quiz.post("/company/{company_id}/quiz/question/option/update", response_model=OptionResponse, tags=["Quizzes"])
async def update_option(company_id: int, option: OptionUpdateScheme,
                          db:AsyncSession = Depends(get_db), current_user:UserResponse =Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            updated_option = await quiz_repository.update_option(option=option)
            return updated_option
        raise HTTPException(status_code=403, detail="You are not allowed to update options")


@router_quiz.post("/company/{company_id}/quiz/{quiz_id}/delete", response_model=DeleteScheme,
                      tags=["Quizzes"])
async def delete_quiz(company_id: int, quiz_id:int,
                        db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            deleted_quiz = await quiz_repository.delete_quiz(quiz_id=quiz_id)
            return deleted_quiz
        raise HTTPException(status_code=403, detail="You are not allowed to delete quizzes")


@router_quiz.post("/company/{company_id}/quiz/question/{question_id}/delete", response_model=DeleteScheme,
                  tags=["Quizzes"])
async def delete_question(company_id: int, question_id:int,
                        db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            deleted_question = await quiz_repository.delete_question(question_id=question_id)
            return deleted_question
        raise HTTPException(status_code=403, detail="You are not allowed to delete question")


@router_quiz.post("/company/{company_id}/quiz/option/{option_id}/delete", response_model=DeleteScheme,
                  tags=["Quizzes"])
async def delete_option(company_id: int, option_id: int,
                        db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        quiz_repository = QuizzRepository(database=db)
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            deleted_question = await quiz_repository.delete_option(option_id=option_id)
            return deleted_question
        raise HTTPException(status_code=403, detail="You are not allowed to delete option")


@router_quiz.post("/company/{company_id}/quiz/{quiz_id}/take-quiz", tags=["Quizzes"])
async def take_quiz(company_id: int, quiz_id: int, questions: List[QuestionTakeQuiz], db:AsyncSession = Depends(get_db),
                    current_user: UserResponse = Depends(get_current_user)) -> dict:
    quizzes_repository = QuizzRepository(database=db)
    ratings = await quizzes_repository.take_quiz(quiz_id=quiz_id, questions=questions, company_id=company_id, user_id=current_user.id)
    return ratings



@router_quiz.get("company/{company_id}/users/averages", tags=["User"])
async def get_all_users_averages(company_id:int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            quiz_result_repository = QuizResultRepository(database=db)
            averages = await quiz_result_repository.get_all_users_averages()
            return averages

@router_quiz.get("company/{company_id}/users/{user_id}/quizzes/averages", tags=["User"], )
async def get_user_quiz_averages(company_id:int, user_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            quiz_result_repository = QuizResultRepository(database=db)
            user_averages = await quiz_result_repository.get_user_quiz_averages(user_id=user_id)
            return user_averages

@router_quiz.get("company/{company_id}/users/last-completions", tags=["Company"])
async def get_company_users_last_completion(company_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    company_repository = CompanyRepository(database=db)
    company = await company_repository.get_company(id=company_id)
    action_repository = ActionRepository(database=db)
    admins = await action_repository.get_all_admins(company_id=company_id, per_page=5, page=1)
    if admins:
        admin_ids = [admin.id for admin in admins.users]
        if company.owner_id == current_user.id or current_user.id in admin_ids:
            quiz_result_repository = QuizResultRepository(database=db)
            last_completions = await quiz_result_repository.get_company_users_last_completion(company_id=company_id)
            return last_completions