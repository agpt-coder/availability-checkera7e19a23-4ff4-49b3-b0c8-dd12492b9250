from datetime import datetime
from enum import Enum
from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class AppointmentDetails(BaseModel):
    """
    Detailed information about each appointment.
    """

    id: int
    scheduledTime: datetime
    status: prisma.enums.AppointmentStatus
    professionalName: str
    professionalId: int


class BookingsResponse(BaseModel):
    """
    Provides a detailed list of all booked appointments for the requesting user or professional, including significant attributes from each appointment.
    """

    appointments: List[AppointmentDetails]


class AppointmentStatus(Enum):
    PENDING: str = "PENDING"
    CONFIRMED: str = "CONFIRMED"
    CANCELLED: str = "CANCELLED"
    COMPLETED: str = "COMPLETED"


async def fetchAppointments(Authorization: str) -> BookingsResponse:
    """
    Retrieves all booked appointments for a logged-in user or professional. This endpoint cross-references user ID with appointment records to provide a personal schedule. It's critical for users and professionals to keep track of their upcoming engagements.

    Args:
        Authorization (str): Bearer Token used to authenticate and authorize user identity.

    Returns:
        BookingsResponse: Provides a detailed list of all booked appointments for the requesting user or professional, including significant attributes from each appointment.
    """
    user_id = int(Authorization.split()[-1])
    appointments = await prisma.models.Appointment.prisma().find_many(
        where={"userId": user_id},
        include={
            "professional": {
                "select": {"profile": {"select": {"firstName": True, "lastName": True}}}
            }
        },
    )
    appointment_details_list = [
        AppointmentDetails(
            id=appointment.id,
            scheduledTime=appointment.scheduledTime,
            status=appointment.status,
            professionalName=f"{appointment.professional.profile.firstName} {appointment.professional.profile.lastName}",
            professionalId=appointment.professionalId,
        )
        for appointment in appointments
    ]
    response = BookingsResponse(appointments=appointment_details_list)
    return response
