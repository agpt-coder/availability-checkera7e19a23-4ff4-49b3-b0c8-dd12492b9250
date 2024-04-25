from datetime import datetime
from typing import List

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


async def getProfessionalProfile(id: int) -> ProfessionalProfileResponse:
    """
    Retrieves the complete profile of a professional by their unique identifier. It extracts data from the
    central database and returns structured information including professional credentials, availability, and
    scheduled appointments. Expected to integrate with security measures to confirm authorization based on role.
    Uses database query functions to fetch the necessary data.

    Args:
        id (int): The unique identifier for the professional.

    Returns:
        ProfessionalProfileResponse: This response model encapsulates the comprehensive professional profile,
        including credentials, availability schedule, and appointments. It aims to provide a JSON-structured
        overview to support front-end rendering or further processing.

    Example:
        profile = await getProfessionalProfile(1)
        print(profile)
    """
    professional = await prisma.models.ProfessionalProfile.prisma().find_unique(
        where={"id": id},
        include={
            "profile": {"include": {"user": True}},
            "availabilities": True,
            "Appointment": True,
        },
    )
    if professional is None:
        raise ValueError(f"No professional found with ID {id}")
    profile_model = ProfessionalProfile(
        profileId=UserProfile(
            bio=professional.profile.bio if professional.profile.bio else ""
        ),
        qualifications=professional.qualifications,
        availabilities=[
            Availability(
                datetime=availability.datetime, isAvailable=availability.isAvailable
            )
            for availability in professional.availabilities
        ],
        appointments=[
            Appointment(
                scheduledTime=appointment.scheduledTime,
                status=prisma.enums.AppointmentStatus(appointment.status),
            )
            for appointment in professional.Appointment
        ],
    )
    return ProfessionalProfileResponse(profile=profile_model)
