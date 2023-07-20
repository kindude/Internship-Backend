

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from repositories.user_repository import UserRepository
from schemas.User import UserScheme, UserResponse, UsersListResponse
from db.get_db import get_db


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
    updated_user = await user_repository.update_user(
        id,
        request.username,
        request.email,
        request.password,
        request.city,
        request.country,
        request.phone,
        request.status,
        request.roles,
    )
    return updated_user


@router.delete("/{id}", response_model=None)
async def delete_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    res = await user_repository.del_user(id)
    if res:
        return {"message": f"{res}"}
    else:
        return {"message": f"No changes to the db"}

@router.get("/all")
async def get_all(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)) -> UsersListResponse:
    user_repository = UserRepository(database=db)
    response = await user_repository.get_users(page=page, per_page=per_page)
    return response


@router.get("/{id}", response_model=UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(database=db)
    query = await user_repository.get_user(id)
    return query