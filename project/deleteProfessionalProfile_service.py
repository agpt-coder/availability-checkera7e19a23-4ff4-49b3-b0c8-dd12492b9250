from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class DeleteProfessionalResponse(BaseModel):
    """
    Response model indicating the result of the delete operation on a professional's profile. It returns a success message or an error message upon failure.
    """

    confirmation: str
    error: Optional[str] = None


async def deleteProfessionalProfile(id: int) -> DeleteProfessionalResponse:
    """
    Permits authorized users to delete a professional's profile using the professional's ID. The endpoint removes the profile from the database and informs the Notification System to update all relevant parties about the deletion. A successful operation returns a confirmation, while failure results in an error message.

    Args:
    id (int): The unique identifier of the professional whose profile is to be deleted.

    Returns:
    DeleteProfessionalResponse: Response model indicating the result of the delete operation on a professional's profile. It returns a success message or an error message upon failure.
    """
    try:
        profile = await prisma.models.ProfessionalProfile.prisma().find_unique(
            where={"id": id}
        )
        if profile is None:
            return DeleteProfessionalResponse(
                confirmation="", error="Professional profile not found."
            )
        await prisma.models.Availability.prisma().delete_many(
            where={"professionalId": id}
        )
        await prisma.models.Appointment.prisma().delete_many(
            where={"professionalId": id}
        )
        await prisma.models.Review.prisma().delete_many(where={"professionalId": id})
        await prisma.models.ProfessionalProfile.prisma().delete(where={"id": id})
        notification_message = f"Professional Profile with ID {id} has been deleted."
        await prisma.models.Notification.prisma().create(
            data={"userId": profile.profileId, "message": notification_message}
        )
        return DeleteProfessionalResponse(
            confirmation="Professional profile successfully deleted."
        )
    except Exception as e:
        return DeleteProfessionalResponse(
            confirmation="", error=f"Failed to delete professional profile: {str(e)}"
        )
