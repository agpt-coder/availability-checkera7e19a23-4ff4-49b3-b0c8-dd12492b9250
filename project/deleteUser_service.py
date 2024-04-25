import prisma
import prisma.models
from pydantic import BaseModel


class DeleteUserResponse(BaseModel):
    """
    This response model sends back a confirmation message indicating whether the deletion was successful or if there were any errors.
    """

    message: str


async def deleteUser(userId: int) -> DeleteUserResponse:
    """
    Removes a user from the system based on user ID. This endpoint will also handle cleanup of any relational data in other modules where applicable, such as posts or comments linked to the user. Only Admin can perform this action.

    Args:
        userId (int): The unique identifier of the user to be deleted.

    Returns:
        DeleteUserResponse: This response model sends back a confirmation message indicating whether the deletion was successful or if there were any errors.

    Example:
        deleteUser(5)
        > DeleteUserResponse(message="User and related data deleted successfully.")
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": userId})
    if not user:
        return DeleteUserResponse(message="User does not exist.")
    await prisma.models.Appointment.prisma().delete_many(where={"userId": userId})
    await prisma.models.Notification.prisma().delete_many(where={"userId": userId})
    if user.profile:
        if user.profile.professional:
            await prisma.models.Availability.prisma().delete_many(
                where={"professionalId": user.profile.professional.id}
            )
            await prisma.models.Appointment.prisma().delete_many(
                where={"professionalId": user.profile.professional.id}
            )
            await prisma.models.Review.prisma().delete_many(
                where={"professionalId": user.profile.professional.id}
            )
            await prisma.models.ProfessionalProfile.prisma().delete(
                where={"id": user.profile.professional.id}
            )
        await prisma.models.UserProfile.prisma().delete(where={"id": user.profile.id})
    await prisma.models.User.prisma().delete(where={"id": userId})
    return DeleteUserResponse(message="User and related data deleted successfully.")
