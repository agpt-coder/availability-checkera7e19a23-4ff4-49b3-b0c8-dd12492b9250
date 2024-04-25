from datetime import date, datetime
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


async def checkAvailability(
    professionalId: Optional[int], date: Optional[date]
) -> AvailabilityResponse:
    """
    This function retrieves the current availability status of professionals. It queries the database for the latest statuses updated by the Notification System and provides a real-time view. The response includes an array of professionals with their current availability status. This endpoint is crucial for the Interactive Scheduling module to display up-to-date information.

    Args:
    professionalId (Optional[int]): Filter to fetch availability for a specific professional using their ID. This is optional.
    date (Optional[date]): Filter availability by specific date. This is optional.

    Returns:
    AvailabilityResponse: Response model for getting availability statuses of professionals. Returns an array of professional profiles with their current availability status.

    Example:
        checkAvailability(1, date(2023, 9, 10))
        > AvailabilityResponse(availabilities=[...])
    """
    availability_query = {}
    if professionalId is not None:
        availability_query["professional"] = {"some": {"id": professionalId}}
    if date is not None:
        day_start = datetime.combine(date, datetime.min.time())
        day_end = datetime.combine(date, datetime.max.time())
        availability_query["datetime"] = {"gte": day_start, "lt": day_end}
    availabilities = await prisma.models.Availability.prisma().find_many(
        where=availability_query,
        include={"professional": {"include": {"profile": True}}},
    )
    availability_profiles = []
    for availability in availabilities:
        professional = availability.professional.profile
        availability_profiles.append(
            ProfessionalAvailability(
                professionalId=professional.id,
                name=f"{professional.firstName} {professional.lastName}",
                availability=availability.isAvailable,
                nextAvailableTime=availability.datetime
                if availability.isAvailable
                else None,
            )
        )
    return AvailabilityResponse(availabilities=availability_profiles)
