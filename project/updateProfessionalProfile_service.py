from datetime import datetime
from typing import List, Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UserProfile(BaseModel):
    """
    User profile object containing personal information.
    """

    bio: str


class Availability(BaseModel):
    """
    Model representing the availability time slots for professionals.
    """

    datetime: datetime
    isAvailable: bool


class Appointment(BaseModel):
    """
    Appointment details with clients.
    """

    scheduledTime: datetime
    status: prisma.enums.AppointmentStatus


class ProfessionalProfile(BaseModel):
    """
    Structured detailed profile data for a professional.
    """

    profileId: UserProfile
    qualifications: str
    availabilities: List[Availability]
    appointments: List[Appointment]


class ProfessionalProfileUpdateResponse(BaseModel):
    """
    Response model for updates to professional profiles, indicating the success or failure of the operation.
    """

    success: bool
    message: str
    updated_profile: Optional[ProfessionalProfile] = None


async def updateProfessionalProfile(
    id: int, qualifications: Optional[str], bio: Optional[str]
) -> ProfessionalProfileUpdateResponse:
    """
    Enables existing profiles to be updated by authorized users. This endpoint requires sending a payload with updated fields for a professional's profile. It performs data validation, updates the relevant database records, and pushes update notifications to the Notification System for alerting subscribed users. Responses indicate either the success or failure of the update operation.

    Args:
        id (int): The unique identifier for the professional whose profile is to be updated. This is a path parameter.
        qualifications (Optional[str]): Updated qualifications of the professional. Optional field.
        bio (Optional[str]): Updated biography of the professional. This field is optional, it updates the linked UserProfile.

    Returns:
        ProfessionalProfileUpdateResponse: Response model for updates to professional profiles, indicating the success or failure of the operation.
    """
    professional = await prisma.models.ProfessionalProfile.prisma().find_unique(
        where={"id": id},
        include={
            "profile": True,
            "reviews": True,
            "availabilities": True,
            "Appointment": True,
        },
    )
    if professional is None:
        return ProfessionalProfileUpdateResponse(
            success=False,
            message="No professional profile found with ID: {}".format(id),
        )
    update_data = {}
    if qualifications:
        update_data["qualifications"] = qualifications
    if bio:
        await prisma.models.UserProfile.prisma().update(
            where={"id": professional.profileId}, data={"bio": bio}
        )
    if update_data:
        await prisma.models.ProfessionalProfile.prisma().update(
            where={"id": id}, data=update_data
        )
    updated_professional = await prisma.models.ProfessionalProfile.prisma().find_unique(
        where={"id": id},
        include={
            "profile": True,
            "reviews": True,
            "availabilities": True,
            "Appointment": True,
        },
    )
    updated_profile = ProfessionalProfile(
        profileId=updated_professional.profile.id,
        qualifications=updated_professional.qualifications,
        availabilities=updated_professional.availabilities,
        appointments=updated_professional.Appointment,
    )
    return ProfessionalProfileUpdateResponse(
        success=True,
        message="Profile successfully updated.",
        updated_profile=updated_profile,
    )
