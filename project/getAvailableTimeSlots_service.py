from datetime import datetime
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class ProfessionalAvailability(BaseModel):
    """
    Consists of professional details and their current availability status.
    """

    professionalId: int
    name: str
    availability: bool
    nextAvailableTime: Optional[datetime] = None


class AvailabilityResponse(BaseModel):
    """
    Response model for getting availability statuses of professionals. Returns an array of professional profiles with their current availability status.
    """

    availabilities: List[ProfessionalAvailability]


async def getAvailableTimeSlots(
    professionalId: int, start_date: datetime, end_date: datetime
) -> AvailabilityResponse:
    """
    Fetches real-time available time slots for professionals. This endpoint queries the Real-time Availability Tracking module to receive updated data and presents it to the user. Responses include a list of time blocks showing availability status.

    Args:
    professionalId (int): The identifier for the professional whose availability is being checked.
    start_date (datetime): The starting date from which to check availability.
    end_date (datetime): The end date to which availability checking extends.

    Returns:
    AvailabilityResponse: Response model for getting availability statuses of professionals. Returns an array of professional profiles with their current availability status.
    """
    professional = await prisma.models.ProfessionalProfile.prisma().find_unique(
        where={"id": professionalId},
        include={
            "profile": True,
            "availabilities": {
                "where": {
                    "datetime": {"gte": start_date, "lte": end_date},
                    "professionalId": professionalId,
                }
            },
        },
    )
    if not professional:
        return AvailabilityResponse(availabilities=[])
    availability_list = []
    for availability in professional.availabilities:
        availability_list.append(
            ProfessionalAvailability(
                professionalId=professionalId,
                name=f"{professional.profile.firstName} {professional.profile.lastName}",
                availability=availability.isAvailable,
                nextAvailableTime=availability.datetime
                if availability.isAvailable
                else None,
            )
        )
    return AvailabilityResponse(availabilities=availability_list)
