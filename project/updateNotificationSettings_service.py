from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class PatchNotificationSettingsResponse(BaseModel):
    """
    Response model confirming the updates made to a user's notification settings.
    """

    success: bool
    updatedFields: List[str]
    userId: str


async def updateNotificationSettings(
    userId: str,
    emailNotificationsEnabled: Optional[bool],
    pushNotificationsEnabled: Optional[bool],
    weeklySummaryEnabled: Optional[bool],
    promotionNotificationsEnabled: Optional[bool],
) -> PatchNotificationSettingsResponse:
    """
    Allows users to modify their notification settings, adapting how and when they receive different types of notifications.
    This endpoint supports partial updates to accommodate flexibility in user choices and minimal bandwidth usage.
    Authentication and appropriate authorization checks ensure that users can only affect their settings.

    Args:
        userId (str): The ID of the user whose notification settings are being updated.
        emailNotificationsEnabled (Optional[bool]): Option to enable or disable email notifications.
        pushNotificationsEnabled (Optional[bool]): Option to enable or disable push notifications.
        weeklySummaryEnabled (Optional[bool]): Option to enable or disable weekly summary emails.
        promotionNotificationsEnabled (Optional[bool]): Option to enable or disable promotional notifications.

    Returns:
        PatchNotificationSettingsResponse: Response model confirming the updates made to a user's notification settings.
    """
    user = await prisma.models.User.prisma().find_unique(where={"id": int(userId)})
    if not user:
        return PatchNotificationSettingsResponse(
            success=False, updatedFields=[], userId=userId
        )
    updated_fields = []
    if emailNotificationsEnabled is not None:
        await prisma.models.Notification.prisma().update_many(
            where={"userId": int(userId)},
            data={"emailNotifications": emailNotificationsEnabled},
        )
        updated_fields.append("emailNotificationsEnabled")
    if pushNotificationsEnabled is not None:
        await prisma.models.Notification.prisma().update_many(
            where={"userId": int(userId)},
            data={"pushNotifications": pushNotificationsEnabled},
        )
        updated_fields.append("pushNotificationsEnabled")
    if weeklySummaryEnabled is not None:
        await prisma.models.Notification.prisma().update_many(
            where={"userId": int(userId)}, data={"weeklySummary": weeklySummaryEnabled}
        )
        updated_fields.append("weeklySummaryEnabled")
    if promotionNotificationsEnabled is not None:
        await prisma.models.Notification.prisma().update_many(
            where={"userId": int(userId)},
            data={"promotionNotifications": promotionNotificationsEnabled},
        )
        updated_fields.append("promotionNotificationsEnabled")
    return PatchNotificationSettingsResponse(
        success=True, updatedFields=updated_fields, userId=userId
    )
