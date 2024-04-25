from datetime import datetime
from typing import Optional

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class Appointment(BaseModel):
    """
    Appointment details with clients.
    """

    scheduledTime: datetime
    status: prisma.enums.AppointmentStatus


class UpdateAppointmentResponse(BaseModel):
    """
    Outputs the result of updating the appointment, including the final state of the appointment and any relevant messages or errors.
    """

    success: bool
    message: str
    updatedAppointment: Appointment
    notification: prisma.models.Notification


class AppointmentStatus:
    """
    Enum representing the status of an appointment.
    """

    PENDING: str = "PENDING"
    CONFIRMED: str = "CONFIRMED"
    CANCELLED: str = "CANCELLED"
    COMPLETED: str = "COMPLETED"


async def updateAppointment(
    appointmentId: int,
    newScheduledTime: Optional[datetime],
    status: prisma.enums.AppointmentStatus,
) -> UpdateAppointmentResponse:
    """
    Provides the functionality to update an existing appointment. Users can change the time or cancel the appointment. Changes are reflected across the Real-time Availability Tracker and should update the prisma.models.Notification System accordingly.

    Args:
        appointmentId (int): Unique identifier of the appointment to update.
        newScheduledTime (Optional[datetime]): New date and time for the appointment, if being rescheduled. Nullable if canceled.
        status (prisma.enums.AppointmentStatus): New status of the appointment, typically updated when cancelation or confirmation occurs.

    Returns:
        UpdateAppointmentResponse: Outputs the result of updating the appointment, including the final state of the appointment and any relevant messages or errors.
    """
    try:
        appointment = await prisma.models.Appointment.prisma().find_unique(
            where={"id": appointmentId}
        )
        if not appointment:
            return UpdateAppointmentResponse(
                success=False,
                message="Appointment not found.",
                updatedAppointment=None,
                notification=None,
            )
        update_data = {"status": status}
        if newScheduledTime:
            update_data["scheduledTime"] = newScheduledTime
        updated_appointment = await prisma.models.Appointment.prisma().update(
            where={"id": appointmentId}, data=update_data
        )
        notification = await prisma.models.Notification.prisma().create(
            data={
                "userId": updated_appointment.userId,
                "message": f"Appointment status updated to {status}.",
                "createdAt": datetime.now(),
                "isRead": False,
            }
        )
        return UpdateAppointmentResponse(
            success=True,
            message="Appointment updated successfully.",
            updatedAppointment=updated_appointment,
            notification=notification,
        )
    except Exception as e:
        return UpdateAppointmentResponse(
            success=False,
            message=f"Error updating appointment: {str(e)}",
            updatedAppointment=None,
            notification=None,
        )
