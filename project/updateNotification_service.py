from typing import Any, Dict

import prisma
import prisma.models
from pydantic import BaseModel


class UpdateNotificationResponse(BaseModel):
    """
    Outputs the updated details of the notification after the PUT operation, confirming the changes made.
    """

    success: bool
    notificationId: int
    updatedFields: Dict[str, Any]


async def updateNotification(
    notificationId: int, message: str, isRead: bool
) -> UpdateNotificationResponse:
    """
    Updates the details of a specific notification. Only accessible by admins, this endpoint is used for managing
    notification statuses or correcting information. The notification's ID is required to fetch the correct entity,
    and modifications are restricted to only certain fields to maintain data integrity.

    Args:
        notificationId (int): The unique identifier of the notification to be updated.
        message (str): The new message content for the notification, if it needs to be updated.
        isRead (bool): A new state indicating whether the notification has been read. This helps in maintaining the read status.

    Returns:
        UpdateNotificationResponse: Outputs the updated details of the notification after the PUT operation, confirming the changes made.
    """
    notification = await prisma.models.Notification.prisma().find_unique(
        where={"id": notificationId}
    )
    if notification is None:
        return UpdateNotificationResponse(
            success=False, notificationId=notificationId, updatedFields={}
        )
    updated_notification = await prisma.models.Notification.prisma().update(
        where={"id": notificationId}, data={"message": message, "isRead": isRead}
    )
    fields_updated = {}
    if message != notification.message:
        fields_updated["message"] = message
    if isRead != notification.isRead:
        fields_updated["isRead"] = isRead
    return UpdateNotificationResponse(
        success=True, notificationId=notificationId, updatedFields=fields_updated
    )
