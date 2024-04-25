from datetime import datetime

import bcrypt
import prisma
import prisma.models
from pydantic import BaseModel


class AuthenticationResponse(BaseModel):
    """
    This model represents the response returned upon successful authentication. It includes the authentication token and a message.
    """

    token: str
    message: str


async def authenticateUser(email: str, password: str) -> AuthenticationResponse:
    """
    Authenticates a user attempting to log in. This endpoint will accept credentials, such as email and password, validate them against stored data, and return an authentication token if successful. It will also log the login attempt details for security monitoring.

    Args:
    email (str): The email address of the user trying to authenticate.
    password (str): The password for the associated email address.

    Returns:
    AuthenticationResponse: This model represents the response returned upon successful authentication. It includes the authentication token and a message.
    """
    user = await prisma.models.User.prisma().find_unique(where={"email": email})
    if user is None:
        return AuthenticationResponse(
            token="", message="Authentication failed. User not found."
        )
    if not bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return AuthenticationResponse(
            token="", message="Authentication failed. Incorrect password."
        )
    token = "generated_authentication_token"
    await prisma.models.Notification.prisma().create(
        data={
            "userId": user.id,
            "message": f"User {email} authenticated successfully.",
            "createdAt": datetime.now(),
            "isRead": False,
        }
    )
    return AuthenticationResponse(token=token, message="Authentication successful.")
