from enum import Enum

import bcrypt
import prisma
import prisma.models
from pydantic import BaseModel


class Role(Enum):
    """
    Role enumeration providing different user roles.
    """

    role: enum  # TODO(autogpt): F821 Undefined name `enum`


class CreateUserResponse(BaseModel):
    """
    This model represents the response returned after successfully creating a new user. It includes the user ID of the newly created account.
    """

    user_id: int


async def createUser(email: str, password: str, role: Role) -> CreateUserResponse:
    """
    Creates a new user account. This endpoint will accept user details, such as email, password, and role, and will create a new user in the database. The password will be hashed for security. All user data validation is performed before insertion. After successful creation, it returns the user id of the newly created user.

    Args:
        email (str): Email address for the new user, must be unique.
        password (str): Plain text password that will be hashed before storage.
        role (Role): The role of the new user, restricted to specific predefined roles.

    Returns:
        CreateUserResponse: This model represents the response returned after successfully creating a new user. It includes the user ID of the newly created account.
    """
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    created_user = await prisma.models.User.prisma().create(
        data={"email": email, "password": hashed_password, "role": role.name}
    )
    return CreateUserResponse(user_id=created_user.id)
