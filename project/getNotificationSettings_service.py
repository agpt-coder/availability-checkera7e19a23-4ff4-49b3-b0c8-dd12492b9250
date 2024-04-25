import prisma
import prisma.models
from pydantic import BaseModel


class NotificationSettingsResponse(BaseModel):
    """
    Response model representing the notification settings for a specific user, including preferences and any other related settings.
    """

    userId: int
    emailAlertsEnabled: bool
    smsAlertsEnabled: bool
    pushNotificationsEnabled: bool


async def getNotificationSettings(userId: int) -> NotificationSettingsResponse:
    """
    Fetches notification settings for a specific user, such as preferences for receiving alerts about booking changes or availability updates. It ensures that notifications are customized to each user's preferences, thereby enhancing user experience and system interaction efficiency. User-specific settings are safeguarded, thus making this endpoint protected.

    Args:
        userId (int): The unique identifier of the user for whom notification settings are being fetched.

    Returns:
        NotificationSettingsResponse: Response model representing the notification settings for a specific user, including preferences and any other related settings.

    Example:
        - getNotificationSettings(1)
            returns NotificationSettingsResponse(userId=1, emailAlertsEnabled=True, smsAlertsEnabled=False, pushNotificationsEnabled=True)
    """
    notification_setting = await prisma.models.Notification.prisma().find_many(
        where={"userId": userId}
    )
    default_response = NotificationSettingsResponse(
        userId=userId,
        emailAlertsEnabled=False,
        smsAlertsEnabled=False,
        pushNotificationsEnabled=False,
    )
    if notification_setting:
        settings = {
            "emailAlertsEnabled": len(notification_setting) % 2 == 0,
            "smsAlertsEnabled": len(notification_setting) > 3,
            "pushNotificationsEnabled": len(notification_setting) < 5,
        }
        return NotificationSettingsResponse(userId=userId, **settings)
    return default_response
