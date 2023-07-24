from http.client import HTTPException

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.User import User
from repositories.user_repository import UserRepository
from schemas.User import UserScheme, UserResponse, UsersListResponse, UserDeleteScheme, UserLogin, Token
from db.get_db import get_db
from utils.auth import get_user_by_token
from utils.auth import get_current_user
router = APIRouter()



@router.post("/create", response_model=UserResponse)
async def create_user(request: UserScheme, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    user = await user_repository.create_user(request=request)

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



@router.post("/updateUser/{id}", response_model=UserResponse)
async def update_user(id:int, request: UserScheme, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    updated_user = await user_repository.update_user(id=id, request=request)
    return updated_user


@router.delete("/{id}", response_model=UserDeleteScheme)
async def delete_user(id: int, db: AsyncSession = Depends(get_db)) -> UserDeleteScheme:
    user_repository = UserRepository(database=db)
    res = await user_repository.del_user(id=id)
    return res

@router.get("/all")
async def get_all(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)) -> UsersListResponse:
    user_repository = UserRepository(database=db)
    response = await user_repository.get_users(page=page, per_page=per_page)
    return response


@router.get("/{id}", response_model=UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user(id=id)
    return query


@router.post("/me", response_model=UserScheme)
async def get_user(request: Token) -> UserScheme:
    user = get_user_by_token(request=request)
    return user


@router.get("/username/{username}", response_model=UserScheme)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)) -> UserScheme:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user_by_username(username=username)
    return query


@router.post("/login", response_model=str)
async def user_login(request: UserLogin, db: AsyncSession = Depends(get_db))->str:
    user_repository = UserRepository(database=db)
    res = await user_repository.authenticate_user(request=request)
    return res

@router.post("/api/secure", response_model=dict)
async def secure_route(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> dict:
    user_repository = UserRepository(database=db)
    # await user_repository.create_blank_user(current_user["email"])
    return {"message": "Доступ разрешен", "user": current_user}


@router.put("/users/me", response_model=UserScheme)
async def update_user_profile(user_data: UserScheme, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Check if the current user is editing their own profile
    if current_user.username != user_data.username:
        raise HTTPException(status_code=403, detail="You can only edit your own profile")

    if current_user.email != user_data.email:
        raise HTTPException(status_code=403, detail="You cannot change your email")


    user_repository = UserRepository(database=db)
    updated_user = await user_repository.update_user_profile(current_user.id, user_data)

    return updated_user

@router.put("/users/me/password", response_model=UserScheme)
async def update_user_password(new_password: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    if new_password == current_user.password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
    user_repository = UserRepository(database=db)

    updated_user = await user_repository.update_user_password(current_user.id, new_password)

    return updated_user


@router.delete("/users/me", response_model=dict)
async def delete_user_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(database=db)
    deleted_user = await user_repository.delete_user(current_user.id)

    return {"message": "User profile deleted successfully"}
