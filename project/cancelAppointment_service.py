import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class CancelBookingResponse(BaseModel):
    """
    Response model for the cancellation of a booking. Provides confirmation that the appointment has been cancelled and the related entities, Availability and Notification, have been updated.
    """

    success: bool
    message: str


async def cancelAppointment(appointment_id: int) -> CancelBookingResponse:
    """
    This endpoint allows users to cancel a booked appointment. It updates the appointment status, frees up the reserved time slot in the Real-time Availability Tracker, and notifies the user and professional via the Notification System.

    Args:
        appointment_id (int): The unique identifier for the appointment that is intended to be cancelled.

    Returns:
        CancelBookingResponse: Response model for the cancellation of a booking. Provides confirmation that the appointment has been cancelled and the related entities, Availability and Notification, have been updated.

    Example:
        cancelAppointment(101)
        > CancelBookingResponse(success=True, message="The appointment has been successfully cancelled.")
    """
    appointment = await prisma.models.Appointment.prisma().find_unique(
        where={"id": appointment_id}
    )
    if appointment is None:
        return CancelBookingResponse(success=False, message="Appointment not found.")
    if appointment.status == prisma.enums.AppointmentStatus.CANCELLED:
        return CancelBookingResponse(
            success=False, message="Appointment is already cancelled."
        )
    updated_appointment = await prisma.models.Appointment.prisma().update(
        where={"id": appointment_id},
        data={"status": prisma.enums.AppointmentStatus.CANCELLED},
    )
    await prisma.models.Availability.prisma().update_many(
        where={
            "datetime": updated_appointment.scheduledTime,
            "professionalId": updated_appointment.professionalId,
        },
        data={"isAvailable": True},
    )
    user_notification = {
        "userId": updated_appointment.userId,
        "message": "Your appointment has been cancelled.",
    }
    professional_notification = {
        "userId": updated_appointment.professionalId,
        "message": "An appointment has been cancelled.",
    }
    await prisma.models.Notification.prisma().create_many(
        data=[user_notification, professional_notification]
    )
    return CancelBookingResponse(
        success=True, message="The appointment has been successfully cancelled."
    )
