import datetime
import os

from jose import jwt

from schemas.User import UserResponse

from ENV import SECRET_KEY


def create_token(user: UserResponse):

    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)

    payload = {
        "username": user.username,
        "email": user.email,
        "exp": expiration
    }
    algorithm = os.getenv("ALGORITHM")

    token = jwt.encode(payload, SECRET_KEY, algorithm=algorithm)

    return token
