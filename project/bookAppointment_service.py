from datetime import datetime
from typing import Optional

import prisma
import prisma.models
from pydantic import BaseModel


class BookingResponse(BaseModel):
    """
    Model for the response after attempting to book an appointment. It contains the outcome of the booking request.
    """

    success: bool
    message: str
    appointmentId: Optional[int] = None


async def bookAppointment(
    userId: int, professionalId: int, scheduledTime: datetime
) -> BookingResponse:
    """
    Allows users to book appointments with professionals. The endpoint checks slot availability via the Real-time Availability Tracker, reserves the chosen slot, and then updates the appointment schedules. A successful booking triggers notifications via the Notification System.

    Args:
    userId (int): The unique identifier for the user trying to make a booking.
    professionalId (int): The unique identifier for the professional with whom the appointment is to be booked.
    scheduledTime (datetime): The requested date and time for the appointment.

    Returns:
    BookingResponse: Model for the response after attempting to book an appointment. It contains the outcome of the booking request.
    """
    availability = await prisma.models.Availability.prisma().find_first(
        where={
            "professionalId": professionalId,
            "datetime": scheduledTime,
            "isAvailable": True,
        }
    )
    if not availability:
        return BookingResponse(
            success=False, message="No available slots at the requested time."
        )
    try:
        new_appointment = await prisma.models.Appointment.prisma().create(
            data={
                "userId": userId,
                "professionalId": professionalId,
                "scheduledTime": scheduledTime,
            }
        )
    except Exception as e:
        return BookingResponse(success=False, message=str(e))
    await prisma.models.Availability.prisma().update(
        where={"id": availability.id}, data={"isAvailable": False}
    )
    await prisma.models.Notification.prisma().create(
        data={
            "userId": professionalId,
            "message": f"New appointment booked for {scheduledTime}",
        }
    )
    return BookingResponse(
        success=True,
        message="Appointment booked successfully.",
        appointmentId=new_appointment.id,
    )
