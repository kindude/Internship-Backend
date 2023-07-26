import datetime
import os
from http.client import HTTPException

import jwt
from fastapi.security import OAuth2PasswordBearer


from ENV import SECRET_KEY, CLIENT_SECRET, ALGORITHM, API_AUDIENCE


from schemas.User import UserResponse, UserScheme, Token, UserToken

from fastapi import Depends, HTTPException
from jose import jwt, JWTError


def create_token(user: UserResponse):
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

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


def get_user_by_token(request: Token) -> UserToken:
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=["HS256"])

        username: str = payload.get("username")
        email: str = payload.get("email")

        if username is not None:
            return UserToken(
                username=username,
                email=email,
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    payload = jwt.decode(token, CLIENT_SECRET, algorithms=ALGORITHM, audience=API_AUDIENCE, options={"verify_signature": False})
    email = payload.get('email')
    return email