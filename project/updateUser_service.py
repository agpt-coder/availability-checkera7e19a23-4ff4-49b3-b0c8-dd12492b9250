from typing import Optional

import bcrypt
import prisma
import prisma.models
from pydantic import BaseModel


class UserUpdateResponse(BaseModel):
    """
    Response model for updating a user's details. Returns the updated user profile data.
    """

    userId: int
    email: str
    firstName: str
    lastName: str
    bio: Optional[str] = None


async def updateUser(
    userId: int,
    email: Optional[str],
    password: Optional[str],
    firstName: Optional[str],
    lastName: Optional[str],
    bio: Optional[str],
) -> UserUpdateResponse:
    """
    Updates user details for a specific user ID. This can include changes to email, password, and any profile data linked to the user's role. The request must be authenticated, and users can only update their own profiles unless they are Admins. Password updates should re-hash the new password.

    Args:
        userId (int): The unique identifier for the user whose details are to be updated. This is a path parameter.
        email (Optional[str]): The new email address for the user. Optional, provide only if updating.
        password (Optional[str]): The new password for the user. If provided, it will be hashed before storage. Optional, provide only if updating.
        firstName (Optional[str]): The user's new first name. Optional, provide only if updating.
        lastName (Optional[str]): The user's new last name. Optional, provide only if updating.
        bio (Optional[str]): The user's new biography text. Optional, provide only if updating.

    Returns:
        UserUpdateResponse: Response model for updating a user's details. Returns the updated user profile data.
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": userId}, include={"profile": True}
    )
    if not user:
        raise ValueError("User not found")
    update_data = {}
    if email:
        update_data["email"] = email
    if password:
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        update_data["password"] = hashed_password
    if firstName or lastName or bio:
        profile_data = {}
        if firstName:
            profile_data["firstName"] = firstName
        if lastName:
            profile_data["lastName"] = lastName
        if bio:
            profile_data["bio"] = bio
        update_data["profile"] = {"update": profile_data}
    updated_user = await prisma.models.User.prisma().update(
        where={"id": userId}, data=update_data, include={"profile": True}
    )
    response_data = {
        "userId": updated_user.id,
        "email": updated_user.email,
        "firstName": updated_user.profile.firstName,
        "lastName": updated_user.profile.lastName,
        "bio": updated_user.profile.bio,
    }
    return UserUpdateResponse(**response_data)
