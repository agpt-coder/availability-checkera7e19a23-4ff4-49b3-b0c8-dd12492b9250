from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class AvailabilityUpdateResponse(BaseModel):
    """
    Confirms the status update with the professional's ID and the updated availability status. Also provides any applicable notification message or system feedback.
    """
    professionalId: int  
    updatedStatus: bool  
    message: str

async def updateAvailability(professionalId: int, datetime: datetime, isAvailable: bool) -> AvailabilityUpdateResponse:
    """
    This endpoint allows professionals or admins to update their current status. The function takes a status payload and updates the database. After updating, it sends a signal to the Notification System to propagate changes across the platform. This ensures all connected services like Interactive Scheduling remain synchronized with the latest availability data.

    Args:
    professionalId (int): The unique ID of the professional whose availability is being updated.
    datetime (datetime): The specific date and time for which the availability status is applicable.
    isAvailable (bool): The new availability status to be set. True indicates available, and False indicates not available.

    Returns:
    AvailabilityUpdateResponse: Confirms the status update with the professional's ID and the updated availability status. Also provides any applicable notification message or system feedback.
    """
    availability = await prisma.models.Availability.prisma().find_first(where={'professionalId': professionalId, 'datetime': datetime})
    if availability:
        await prisma.models.Availability.prisma().update_many(where={'id': availability.id}, data={'isAvailable': isAvailable})
    else:
        availability = await prisma.models.Availability.prisma().create(data={'professionalId': professionalId, 'datetime': datetime, 'isAvailable': isAvailable})
    message = f'Your availability for {datetime.strftime('%Y-%m-%d %H:%M')} has been set to {('available' if isAvailable else 'not available')}.'
    await prisma.models.Notification.prisma().create(data={'userId': professionalId, 'message': message, 'createdAt': datetime.utcnow(), 'isRead': False})
    return AvailabilityUpdateResponse(professionalId=professionalId, updatedStatus=isAvailable, message='Availability successfully updated and notification sent.')