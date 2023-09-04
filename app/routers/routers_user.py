from fastapi import HTTPException

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession


from repositories.notification_repository import NotificationRepository

from repositories.quiz_result_repository import QuizResultRepository
from repositories.user_repository import UserRepository

from schemas.User import UserScheme, UserResponse, UsersListResponse, UserDeleteScheme, UserLogin, UserResponseNoPass
from db.get_db import get_db

from utils.auth import get_current_user
router_user = APIRouter()




@router_user.post("/users/register", response_model=UserResponse, tags=["User"])
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


@router_user.put("/users/update/{id}", response_model=UserResponseNoPass, tags=["User"])
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

@router_user.delete("/users/{id}", response_model=UserDeleteScheme, tags=["User"])
async def delete_user(id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)) -> UserDeleteScheme:
    user_repository = UserRepository(database=db)
    if current_user.id != id:
        raise HTTPException(status_code=403, detail="You are not allowed to delete other users' profiles.")

    res = await user_repository.del_user(id=id)
    return res


@router_user.get("/users/all", response_model=UsersListResponse, tags=["User"])
async def get_all(page: int = Query(1, alias="page"), per_page: int = Query(10), db: AsyncSession = Depends(get_db)) -> UsersListResponse:
    user_repository = UserRepository(database=db)
    response = await user_repository.get_users(page=page, per_page=per_page)
    return response


@router_user.get("/users/{id}", response_model=UserResponseNoPass, tags=["User"])
async def get_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponseNoPass:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user(id=id)
    if not query:
        raise HTTPException(status_code=404, detail="User not found")
    return query


@router_user.post("/me", response_model=UserResponse, tags=["User"])
async def get_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user


@router_user.get("/users/{username}", response_model=UserResponse, tags=["User"])
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user_by_username(username=username)
    return query


@router_user.post("/users/login", response_model=str, tags=["User"])
async def user_login(request: UserLogin, db: AsyncSession = Depends(get_db)) -> str:
    user_repository = UserRepository(database=db)
    token = await user_repository.authenticate_user(request=request)
    return token.token


@router_user.get("/users/rating", tags=["User"])
async def get_user_rating(db:AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    quiz_result_repository = QuizResultRepository(database=db)

    rating = await quiz_result_repository.calculate_user_averages(user_id=current_user.id)

    return rating["average_system_rating"]


@router_user.get("/quizzes/averages", tags=["User"])
async def get_quiz_averages(db: AsyncSession = Depends(get_db)):
    quiz_result_repository = QuizResultRepository(database=db)
    averages = await quiz_result_repository.get_quiz_averages()
    return averages

@router_user.get("/quizzes/last-completions", tags=["User"])
async def get_last_quiz_completions(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    quiz_result_repository = QuizResultRepository(database=db)
    last_completions = await quiz_result_repository.get_last_quiz_completion(current_user.id)
    return last_completions


@router_user.get("/user/notifications/get", tags=["User"])
async def get_user_notifications(db:AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    notif_repo = NotificationRepository(session=db)
    notifications = await notif_repo.get_notifications(user_id=current_user.id)
    return notifications


@router_user.get("/quizzes/last-completions", tags=["User"])
async def get_last_quiz_completions(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    quiz_result_repository = QuizResultRepository(database=db)
    last_completions = await quiz_result_repository.get_last_quiz_completion(user_id=current_user.id)
    return last_completions
