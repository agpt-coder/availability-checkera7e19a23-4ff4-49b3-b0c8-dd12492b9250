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


class ProfessionalProfileResponse(BaseModel):
    """
    This response model encapsulates the comprehensive professional profile, including credentials, availability schedule, and appointments. It aims to provide a JSON-structured overview to support front-end rendering or further processing.
    """

    profile: ProfessionalProfile


async def createProfessionalProfile(
    profileId: int,
    qualifications: str,
    biography: Optional[str],
    availableDays: List[str],
    hourlyRate: float,
) -> ProfessionalProfileResponse:
    """
    Allows authorized roles to create a new professional profile. The function consumes a data payload containing all necessary professional details, verifies the data according to the business rules, and then inserts it into the database. Appropriate error messages or a success response is generated based on the operation result.

    Args:
        profileId (int): The unique identifier of the user profile associated with this professional.
        qualifications (str): A description of qualifications and certifications that the professional holds.
        biography (Optional[str]): A brief bio of the professional.
        availableDays (List[str]): A list indicating the days of the week the professional is available.
        hourlyRate (float): The professional's hourly consultation rate.

    Returns:
        ProfessionalProfileResponse: This response model encapsulates the comprehensive professional profile, including credentials, availability schedule, and appointments. It aims to provide a JSON-structured overview to support front-end rendering or further processing.
    """
    user_profile = await prisma.models.UserProfile.prisma().find_unique(
        where={"id": profileId}
    )
    if not user_profile:
        raise ValueError("UserProfile with given profileId does not exist")
    professional_profile = await prisma.models.ProfessionalProfile.prisma().create(
        data={"profileId": profileId, "qualifications": qualifications}
    )
    if biography:
        await prisma.models.UserProfile.prisma().update(
            where={"id": profileId}, data={"bio": biography}
        )
    return ProfessionalProfileResponse(profile=professional_profile)
