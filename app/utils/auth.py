import datetime
import os
from http.client import HTTPException

import jwt
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ENV import SECRET_KEY, CLIENT_SECRET, ALGORITHM, API_AUDIENCE, ALGORITHM_AUTH0
from db.get_db import get_db
from repositories.user_repository import UserRepository

from schemas.User import UserResponse, UserScheme, Token, UserToken

from fastapi import Depends, HTTPException
from jose import jwt, JWTError

from services.create_user_scheme import user_scheme_raw_from_data




def get_user_by_token(request: Token) -> UserToken:
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=["HS256"])

        username: str = payload.get("username")
        email: str = payload.get("email")

        if username is not None:
            return UserToken(
                username=username,
                email=email
            )

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_user_email_by_token(request: Token) -> str:
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("username")
        email: str = payload.get("email")
        if not username:
            return None
        return email

    except JWTError:
        try:
            email = get_current_user(request.token)
            return email
        except:
            raise HTTPException(status_code=401, detail="Invalid token")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


security = HTTPBearer()

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return credentials.credentials


async def get_current_user(token: str = Depends(get_token), db: AsyncSession = Depends(get_db)) -> UserResponse:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_signature": False})
        username: str = payload.get("username")
        email: str = payload.get("email")
        if username is None:
            email = None

    except JWTError:
        payload = jwt.decode(token, CLIENT_SECRET, algorithms=["RS256"], audience=API_AUDIENCE, options={"verify_signature": False})
        print(payload)
        email = payload.get('email')


    user_repository = UserRepository(database=db)
    user = await user_repository.get_user_by_email(email=email)
    user_scheme_response = await user_scheme_raw_from_data(user=user, payload=payload, db=user_repository)
    return user_scheme_response


