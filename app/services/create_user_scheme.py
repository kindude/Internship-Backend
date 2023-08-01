from sqlalchemy.ext.asyncio import AsyncSession

from repositories.user_repository import UserRepository
from schemas.User import UserScheme, UserResponse


async def user_scheme_raw_from_data(user, payload,db:UserRepository) -> UserResponse:

    if not user:
        user_to_add = UserScheme(
            email=payload.get("email"),
            username=payload.get("email"),
            password=db.create_password(),
            city="None",
            country="None",
            phone=13 * "0",
            status=True,
            roles=["user"]
        )
        user = await db.create_user(request=user_to_add)
        user = await db.get_user_by_email(user.email)

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


