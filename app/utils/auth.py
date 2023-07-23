import datetime
import os
from http.client import HTTPException

import jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from ENV import SECRET_KEY, auth0_token


from schemas.User import UserResponse, UserScheme, Token

from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
def create_token(user:UserResponse):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)

    payload = {
        "username": user.username,
        "email": user.email,
        # "city": user.city,
        # "country": user.country,
        # "phone": user.phone,
        # "status": user.status,
        # "roles": user.roles,
        "exp": expiration
    }
    algorithm = os.getenv("ALGORITHM")

    token = jwt.encode(payload, SECRET_KEY, algorithm=algorithm)

    return token




oauth2_scheme = OAuth2PasswordBearer(tokenUrl=auth0_token)

def get_user_by_token(token: str = Depends(oauth2_scheme)):
    try:
        algorithm = os.getenv("ALGORITHM")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        username: str = payload.get("username")
        email: str = payload.get("email")

        if username is not None:
            return UserScheme(
                username=username,
                email=email,
                password="ds",
                city="ds",
                country="ds",
                phone="sd",
                status=True,
                roles=["ds", "sd"]
            )

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
