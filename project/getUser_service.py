from enum import Enum
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class Role(Enum):
    """
    Role enumeration providing different user roles.
    """

    role: enum  # TODO(autogpt): F821 Undefined name `enum`


class UserProfile(BaseModel):
    """
    User profile object containing personal information.
    """

    bio: str


class UserDetailsResponse(BaseModel):
    """
    This model details the response structure for a user data request, including personal and professional information if applicable.
    """

    id: int
    email: str
    role: Role
    profile: Optional[UserProfile] = None


async def getUser(userId: int) -> UserDetailsResponse:
    """
    Retrieves the details of an existing user by user ID. It will return user data including e-mail,
    role, and, if applicable, profile information related to the Professional Profile module.
    Only authenticated users can fetch details, and users can only access their own details unless they are an Admin.

    Args:
        userId (int): The unique identifier for the user whose details are to be retrieved.

    Returns:
        UserDetailsResponse: This model details the response structure for a user data request,
        including personal and professional information if applicable.
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": userId}, include={"profile": True}
    )
    if not user:
        raise ValueError(f"User with ID {userId} not found.")
    user_profile = None
    if user.profile:
        user_profile = UserProfile(bio=user.profile.bio)
    user_details = UserDetailsResponse(
        id=user.id, email=user.email, role=Role[user.role], profile=user_profile
    )
    return user_details
