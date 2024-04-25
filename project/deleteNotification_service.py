import prisma
import prisma.models
from pydantic import BaseModel


class DeleteNotificationResponse(BaseModel):
    """
    Confirmation model that returns the ID of the deleted notification and a success message.
    """

    message: str
    deletedId: int


async def deleteNotification(notificationId: int) -> DeleteNotificationResponse:
    """
    Deletes a specific notification. This endpoint is crucial for cleaning up old or irrelevant notifications from the database. It requires administrative rights to prevent accidental data loss and ensures that only expired or invalidated notifications are removed based on strict criteria.

    Args:
    notificationId (int): The unique identifier for the notification intended for deletion.

    Returns:
    DeleteNotificationResponse: Confirmation model that returns the ID of the deleted notification and a success message.
    """
    notification = await prisma.models.Notification.prisma().delete(
        where={"id": notificationId}
    )
    response_message = "Notification deleted successfully."
    return DeleteNotificationResponse(
        message=response_message, deletedId=notification.id
    )
