from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from db.connect import connect_Postgre
from repositories.user_repository import UserRepository
from schemas.User import User, UserResponse

router = APIRouter()

async_session = None

async def get_db():
    async_session = await connect_Postgre()
    try:
        yield async_session
    finally:
        await async_session.close()


@router.post("/create")
async def create_user(request: User, db: AsyncSession = Depends(get_db)) -> User:
    user_repository = UserRepository(db)
    await user_repository.create_user(
        username=request.username,
        email=request.email,
        password=request.password,
        city=request.city,
        country=request.country,
        phone=request.phone,
        status=request.status,
        roles=request.roles,
    )
    return request


@router.delete("/{id}")
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    await user_repository.del_user(id)
    return {"message": f"User with id:{id} was removed"}


@router.post("/updateUser")
async def update_user(request: User, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    await user_repository.update_user(
        request.id, request.username, request.email, request.password, request.city, request.country,
        request.phone, request.status, request.roles
    )
    return {"message": f"User with id {request.id} has been successfully updated"}


@router.get("/all")
async def get_all(page: int = 1, per_page: int = 10, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    response = await user_repository.get_users(page=page, per_page=per_page)
    return response


@router.get("/{id}", response_model=UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)) -> UserResponse:
    user_repository = UserRepository(db)
    query = await user_repository.get_user(id)
    return query