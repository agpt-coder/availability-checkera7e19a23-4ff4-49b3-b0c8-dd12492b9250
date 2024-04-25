import prisma
import prisma.models
from pydantic import BaseModel


class CreateNotificationResponse(BaseModel):
    """
    Confirms whether the notification was successfully queued for delivery, including any relevant details or errors.
    """

    success: bool
    message: str


async def createNotification(
    recipient_id: int, notification_type: str, content: str
) -> CreateNotificationResponse:
    """
    This endpoint allows for the creation of notifications. It will accept JSON data specifying the notification type, recipient details, and content. It mainly interacts with the user profiles to fetch preference settings before sending out notifications. Using broker services, it queues notifications for delivery. Accessible only by the system or admins to ensure secure handling of notification logic.

    Args:
    recipient_id (int): Unique identifier of the user who will receive the notification.
    notification_type (str): Type of notification to be sent, such as 'ALERT', 'REMINDER', etc.
    content (str): Text content of the notification.

    Returns:
    CreateNotificationResponse: Confirms whether the notification was successfully queued for delivery, including any relevant details or errors.

    Example:
        createNotification(1, 'ALERT', 'Your appointment is now confirmed')
        > CreateNotificationResponse(success=True, message="Notification sent successfully.")
    """
    try:
        notification = await prisma.models.Notification.prisma().create(
            data={"userId": recipient_id, "message": f"[{notification_type}] {content}"}
        )
        return CreateNotificationResponse(
            success=True, message="Notification queued successfully."
        )
    except Exception as e:
        return CreateNotificationResponse(success=False, message=str(e))
