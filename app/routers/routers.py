import hashlib
import os
import redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi import APIRouter, Depends

from app.db import connect_to_postgre, connect_to_redis, asyncSession
from app.models.User import User
from app.repositories.user_repository import UserRepository

router = APIRouter()

connect_to_postgre()
connect_to_redis()


def get_db():
    db = asyncSession()
    try:
        yield db
    finally:
        db.close()


@router.post("/create")
async def create_user(request: User, db: AsyncSession = Depends(get_db)):
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
    return {"message": "User created successfully"}


@router.delete("/{id}")
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    await user_repository.del_user(id)
    return {"message": f"User with id:{id} was removed"}


@router.post("/updateUser")
async def update_user(request: User, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    salt = os.getenv("SALT")
    database_password = request.password + salt
    hashed = hashlib.md5(database_password.encode()).hexdigest()

    await user_repository.update_user(
        request.id, request.username, request.email, hashed, request.city, request.country,
        request.phone, request.status, request.roles
    )

    return {"message": f"User with id {request.id} has been successfully updated"}


@router.get("/all")
async def get_all(db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    response = await user_repository.get_users()
    return {"message": "All users have been successfully retrieved"}


@router.get("/{id}")
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    user_repository = UserRepository(db)
    response = await user_repository.get_user(id)
    return {"message": f"User with id {id} has been successfully retrieved"}
