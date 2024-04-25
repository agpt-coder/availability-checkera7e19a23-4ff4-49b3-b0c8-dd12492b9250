from enum import Enum
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Role(Enum):
    """
    Role enumeration providing different user roles.
    """

    role: enum  # TODO(autogpt): F821 Undefined name `enum`


class UserBasicInfo(BaseModel):
    """
    Basic user information needed for the user listing operation.
    """

    id: int
    email: str
    role: Role


class ListUsersResponse(BaseModel):
    """
    Response model for listing users with basic information. Filtered based on the provided parameters.
    """

    users: List[UserBasicInfo]


async def listUsers(email: Optional[str], role: Optional[Role]) -> ListUsersResponse:
    """
    Lists all users in the system, providing basic user information such as user IDs, email, and roles. It is primarily
    used by Admins for managing users and can also support filtering parameters to refine the list returned.

    Args:
        email (Optional[str]): Optional filter by email to refine the results.
        role (Optional[Role]): Optional filter by role to refine the results.

    Returns:
        ListUsersResponse: Response model for listing users with basic information. Filtered based on the provided parameters.
    """
    where_clause = {}
    if email:
        where_clause["email"] = {"contains": email}
    if role:
        where_clause["role"] = role
    users = await prisma.models.User.prisma().find_many(
        where=where_clause, include={"profile": False}
    )
    user_infos = [
        UserBasicInfo(id=user.id, email=user.email, role=Role[user.role])
        for user in users
    ]
    return ListUsersResponse(users=user_infos)
