import logging
from contextlib import asynccontextmanager
from datetime import date, datetime
from typing import List, Optional

import prisma
import prisma.enums
import project.adminFetchAllBookings_service
import project.authenticateUser_service
import project.bookAppointment_service
import project.cancelAppointment_service
import project.checkAvailability_service
import project.createNotification_service
import project.createProfessionalProfile_service
import project.createUser_service
import project.deleteNotification_service
import project.deleteProfessionalProfile_service
import project.deleteUser_service
import project.fetchAppointments_service
import project.fetchAvailabilityHistory_service
import project.fetchNotifications_service
import project.getAvailableTimeSlots_service
import project.getNotificationSettings_service
import project.getProfessionalProfile_service
import project.getUser_service
import project.listProfessionalProfiles_service
import project.listUsers_service
import project.updateAppointment_service
import project.updateAvailability_service
import project.updateNotification_service
import project.updateNotificationSettings_service
import project.updateProfessionalProfile_service
import project.updateUser_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="Availability Checker",
    lifespan=lifespan,
    description="Function that returns the real-time availability of professionals, updating based on current activity or schedule.",
)


@app.put(
    "/users/{userId}", response_model=project.updateUser_service.UserUpdateResponse
)
async def api_put_updateUser(
    firstName: Optional[str],
    userId: int,
    email: Optional[str],
    password: Optional[str],
    lastName: Optional[str],
    bio: Optional[str],
) -> project.updateUser_service.UserUpdateResponse | Response:
    """
    Updates user details for a specific user ID. This can include changes to email, password, and any profile data linked to the user's role. The request must be authenticated, and users can only update their own profiles unless they are Admins. Password updates should re-hash the new password.
    """
    try:
        res = await project.updateUser_service.updateUser(
            firstName, userId, email, password, lastName, bio
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/users/authenticate",
    response_model=project.authenticateUser_service.AuthenticationResponse,
)
async def api_post_authenticateUser(
    email: str, password: str
) -> project.authenticateUser_service.AuthenticationResponse | Response:
    """
    Authenticates a user attempting to log in. This endpoint will accept credentials, such as email and password, validate them against stored data, and return an authentication token if successful. It will also log the login attempt details for security monitoring.
    """
    try:
        res = await project.authenticateUser_service.authenticateUser(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/api/professional/{id}",
    response_model=project.updateProfessionalProfile_service.ProfessionalProfileUpdateResponse,
)
async def api_put_updateProfessionalProfile(
    id: int, qualifications: Optional[str], bio: Optional[str]
) -> project.updateProfessionalProfile_service.ProfessionalProfileUpdateResponse | Response:
    """
    Enables existing profiles to be updated by authorized users. This endpoint requires sending a payload with updated fields for a professional's profile. It performs data validation, updates the relevant database records, and pushes update notifications to the Notification System for alerting subscribed users. Responses indicate either the success or failure of the update operation.
    """
    try:
        res = await project.updateProfessionalProfile_service.updateProfessionalProfile(
            id, qualifications, bio
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/notifications/settings/{userId}",
    response_model=project.getNotificationSettings_service.NotificationSettingsResponse,
)
async def api_get_getNotificationSettings(
    userId: int,
) -> project.getNotificationSettings_service.NotificationSettingsResponse | Response:
    """
    Fetches notification settings for a specific user, such as preferences for receiving alerts about booking changes or availability updates. It ensures that notifications are customized to each user's preferences, thereby enhancing user experience and system interaction efficiency. User-specific settings are safeguarded, thus making this endpoint protected.
    """
    try:
        res = await project.getNotificationSettings_service.getNotificationSettings(
            userId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/users/{userId}", response_model=project.getUser_service.UserDetailsResponse)
async def api_get_getUser(
    userId: int,
) -> project.getUser_service.UserDetailsResponse | Response:
    """
    Retrieves the details of an existing user by user ID. It will return user data including email, role, and if applicable, profile related to the Professional Profile module. Only authenticated users can fetch details, and users can only access their own details unless they are an Admin.
    """
    try:
        res = await project.getUser_service.getUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/notifications",
    response_model=project.fetchNotifications_service.NotificationsResponse,
)
async def api_get_fetchNotifications(
    user_id: str, role: project.fetchNotifications_service.Role
) -> project.fetchNotifications_service.NotificationsResponse | Response:
    """
    Retrieves a list of notifications for a user. The response includes notification content, type, and status (sent, pending, failed). It filters notifications based on the user ID, authentication status, and role, ensuring only authorized viewing of sensitive data. It's essential for users to review their notifications history and for admins to monitor notification activities.
    """
    try:
        res = project.fetchNotifications_service.fetchNotifications(user_id, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/notifications/{notificationId}",
    response_model=project.deleteNotification_service.DeleteNotificationResponse,
)
async def api_delete_deleteNotification(
    notificationId: int,
) -> project.deleteNotification_service.DeleteNotificationResponse | Response:
    """
    Deletes a specific notification. This endpoint is crucial for cleaning up old or irrelevant notifications from the database. It requires administrative rights to prevent accidental data loss and ensures that only expired or invalidated notifications are removed based on strict criteria.
    """
    try:
        res = await project.deleteNotification_service.deleteNotification(
            notificationId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/api/professional",
    response_model=project.listProfessionalProfiles_service.ProfessionalProfilesListResponse,
)
async def api_get_listProfessionalProfiles(
    request: project.listProfessionalProfiles_service.GetProfessionalProfilesRequest,
) -> project.listProfessionalProfiles_service.ProfessionalProfilesListResponse | Response:
    """
    Fetches a list of all professional profiles. This endpoint is mainly used by administrative roles to monitor and manage professional accounts. It retrieves array-like data structure containing minimal essential details of professionals for quick browsing. Complies with privacy standards by limiting data according to user role access.
    """
    try:
        res = await project.listProfessionalProfiles_service.listProfessionalProfiles(
            request
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/availability/update",
    response_model=project.updateAvailability_service.AvailabilityUpdateResponse,
)
async def api_post_updateAvailability(
    professionalId: int, datetime: datetime, isAvailable: bool
) -> project.updateAvailability_service.AvailabilityUpdateResponse | Response:
    """
    This endpoint allows professionals or admins to update their current status. The function takes a status payload and updates the database. After updating, it sends a signal to the Notification System to propagate changes across the platform. This ensures all connected services like Interactive Scheduling remain synchronized with the latest availability data.
    """
    try:
        res = await project.updateAvailability_service.updateAvailability(
            professionalId, datetime, isAvailable
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/bookings/update",
    response_model=project.updateAppointment_service.UpdateAppointmentResponse,
)
async def api_put_updateAppointment(
    appointmentId: int,
    newScheduledTime: Optional[datetime],
    status: prisma.enums.AppointmentStatus,
) -> project.updateAppointment_service.UpdateAppointmentResponse | Response:
    """
    Provides the functionality to update an existing appointment. Users can change the time or cancel the appointment. Changes are reflected across the Real-time Availability Tracker and should update the Notification System accordingly.
    """
    try:
        res = await project.updateAppointment_service.updateAppointment(
            appointmentId, newScheduledTime, status
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability/history",
    response_model=project.fetchAvailabilityHistory_service.AvailabilityHistoryResponse,
)
async def api_get_fetchAvailabilityHistory(
    professionalId: int,
) -> project.fetchAvailabilityHistory_service.AvailabilityHistoryResponse | Response:
    """
    Fetches the history of availability status changes for a specific professional. This route helps in auditing and tracking the status changes over time. It pulls data from a historical database where past statuses are logged. The response includes time-stamped records of availability updates.
    """
    try:
        res = await project.fetchAvailabilityHistory_service.fetchAvailabilityHistory(
            professionalId
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability",
    response_model=project.getAvailableTimeSlots_service.AvailabilityResponse,
)
async def api_get_getAvailableTimeSlots(
    professionalId: int, start_date: datetime, end_date: datetime
) -> project.getAvailableTimeSlots_service.AvailabilityResponse | Response:
    """
    Fetches real-time available time slots for professionals. This endpoint queries the Real-time Availability Tracking module to receive updated data and presents it to the user. Responses include a list of time blocks showing availability status.
    """
    try:
        res = await project.getAvailableTimeSlots_service.getAvailableTimeSlots(
            professionalId, start_date, end_date
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/bookings/user", response_model=project.fetchAppointments_service.BookingsResponse
)
async def api_get_fetchAppointments(
    Authorization: str,
) -> project.fetchAppointments_service.BookingsResponse | Response:
    """
    Retrieves all booked appointments for a logged-in user or professional. This endpoint cross-references user ID with appointment records to provide a personal schedule. It's critical for users and professionals to keep track of their upcoming engagements.
    """
    try:
        res = await project.fetchAppointments_service.fetchAppointments(Authorization)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/users", response_model=project.listUsers_service.ListUsersResponse)
async def api_get_listUsers(
    email: Optional[str], role: Optional[project.listUsers_service.Role]
) -> project.listUsers_service.ListUsersResponse | Response:
    """
    Lists all users in the system, providing basic user information such as user IDs, email, and roles. It is primarily used by Admins for managing users and can also support filtering parameters to refine the list returned.
    """
    try:
        res = await project.listUsers_service.listUsers(email, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/users/{userId}", response_model=project.deleteUser_service.DeleteUserResponse
)
async def api_delete_deleteUser(
    userId: int,
) -> project.deleteUser_service.DeleteUserResponse | Response:
    """
    Removes a user from the system based on user ID. This endpoint will also handle cleanup of any relational data in other modules where applicable, such as posts or comments linked to the user. Only Admin can perform this action.
    """
    try:
        res = await project.deleteUser_service.deleteUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/admin/bookings",
    response_model=project.adminFetchAllBookings_service.AdminBookingsResponse,
)
async def api_get_adminFetchAllBookings(
    request: project.adminFetchAllBookings_service.AdminBookingsRequest,
) -> project.adminFetchAllBookings_service.AdminBookingsResponse | Response:
    """
    Exclusive to administrators, this endpoint provides a comprehensive overview of all bookings within the system. Useful for high-level management and troubleshooting scheduling conflicts or issues in the platform.
    """
    try:
        res = await project.adminFetchAllBookings_service.adminFetchAllBookings(request)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/api/professional/{id}",
    response_model=project.getProfessionalProfile_service.ProfessionalProfileResponse,
)
async def api_get_getProfessionalProfile(
    id: int,
) -> project.getProfessionalProfile_service.ProfessionalProfileResponse | Response:
    """
    This route retrieves the complete profile of a professional by their unique identifier. It extracts data from the central database and returns structured information including professional credentials, availability, and scheduled appointments. Expected to integrate with security measures to confirm authorization based on role. Uses database query functions to fetch the necessary data.
    """
    try:
        res = await project.getProfessionalProfile_service.getProfessionalProfile(id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/notifications/{notificationId}",
    response_model=project.updateNotification_service.UpdateNotificationResponse,
)
async def api_put_updateNotification(
    notificationId: int, message: str, isRead: bool
) -> project.updateNotification_service.UpdateNotificationResponse | Response:
    """
    Updates the details of a specific notification. Only accessible by admins, this endpoint is used for managing notification statuses or correcting information. The notification's ID is required to fetch the correct entity, and modifications are restricted to only certain fields to maintain data integrity.
    """
    try:
        res = await project.updateNotification_service.updateNotification(
            notificationId, message, isRead
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.patch(
    "/notifications/settings/{userId}",
    response_model=project.updateNotificationSettings_service.PatchNotificationSettingsResponse,
)
async def api_patch_updateNotificationSettings(
    userId: str,
    emailNotificationsEnabled: Optional[bool],
    pushNotificationsEnabled: Optional[bool],
    weeklySummaryEnabled: Optional[bool],
    promotionNotificationsEnabled: Optional[bool],
) -> project.updateNotificationSettings_service.PatchNotificationSettingsResponse | Response:
    """
    Allows users to modify their notification settings, adapting how and when they receive different types of notifications. This endpoint supports partial updates to accommodate flexibility in user choices and minimal bandwidth usage. Authentication and appropriate authorization checks ensure that users can only affect their settings.
    """
    try:
        res = (
            await project.updateNotificationSettings_service.updateNotificationSettings(
                userId,
                emailNotificationsEnabled,
                pushNotificationsEnabled,
                weeklySummaryEnabled,
                promotionNotificationsEnabled,
            )
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/bookings/cancel",
    response_model=project.cancelAppointment_service.CancelBookingResponse,
)
async def api_delete_cancelAppointment(
    appointment_id: int,
) -> project.cancelAppointment_service.CancelBookingResponse | Response:
    """
    This endpoint allows users to cancel a booked appointment. It updates the appointment status, frees up the reserved time slot in the Real-time Availability Tracker, and notifies the user and professional via the Notification System.
    """
    try:
        res = await project.cancelAppointment_service.cancelAppointment(appointment_id)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/api/professional",
    response_model=project.createProfessionalProfile_service.ProfessionalProfileResponse,
)
async def api_post_createProfessionalProfile(
    profileId: int,
    qualifications: str,
    biography: Optional[str],
    availableDays: List[str],
    hourlyRate: float,
) -> project.createProfessionalProfile_service.ProfessionalProfileResponse | Response:
    """
    Allows authorized roles to create a new professional profile. The function consumes a data payload containing all necessary professional details, verifies the data according to the business rules, and then inserts it into the database. Appropriate error messages or a success response is generated based on the operation result.
    """
    try:
        res = await project.createProfessionalProfile_service.createProfessionalProfile(
            profileId, qualifications, biography, availableDays, hourlyRate
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/users", response_model=project.createUser_service.CreateUserResponse)
async def api_post_createUser(
    email: str, password: str, role: project.createUser_service.Role
) -> project.createUser_service.CreateUserResponse | Response:
    """
    Creates a new user account. This endpoint will accept user details, such as email, password, and role, and will create a new user in the database. The password will be hashed for security. All user data validation is performed before insertion. After successful creation, it returns the user id of the newly created user.
    """
    try:
        res = await project.createUser_service.createUser(email, password, role)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/api/professional/{id}",
    response_model=project.deleteProfessionalProfile_service.DeleteProfessionalResponse,
)
async def api_delete_deleteProfessionalProfile(
    id: int,
) -> project.deleteProfessionalProfile_service.DeleteProfessionalResponse | Response:
    """
    Permits authorized users to delete a professional's profile using the professional's ID. The endpoint removes the profile from the database and informs the Notification System to update all relevant parties about the deletion. A successful operation returns a confirmation, while failure results in an error message.
    """
    try:
        res = await project.deleteProfessionalProfile_service.deleteProfessionalProfile(
            id
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/notifications",
    response_model=project.createNotification_service.CreateNotificationResponse,
)
async def api_post_createNotification(
    recipient_id: int, notification_type: str, content: str
) -> project.createNotification_service.CreateNotificationResponse | Response:
    """
    This endpoint allows for the creation of notifications. It will accept JSON data specifying the notification type, recipient details, and content. It mainly interacts with the user profiles to fetch preference settings before sending out notifications. Using broker services, it queues notifications for delivery. Accessible only by the system or admins to ensure secure handling of notification logic.
    """
    try:
        res = await project.createNotification_service.createNotification(
            recipient_id, notification_type, content
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/availability",
    response_model=project.checkAvailability_service.AvailabilityResponse,
)
async def api_get_checkAvailability(
    professionalId: Optional[int], date: Optional[date]
) -> project.checkAvailability_service.AvailabilityResponse | Response:
    """
    This route retrieves the current availability status of professionals. It queries the database for the latest statuses updated by the Notification System and provides a real-time view. The response includes an array of professionals with their current availability status. This endpoint is crucial for the Interactive Scheduling module to display up-to-date information.
    """
    try:
        res = await project.checkAvailability_service.checkAvailability(
            professionalId, date
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/bookings", response_model=project.bookAppointment_service.BookingResponse)
async def api_post_bookAppointment(
    userId: int, professionalId: int, scheduledTime: datetime
) -> project.bookAppointment_service.BookingResponse | Response:
    """
    Allows users to book appointments with professionals. The endpoint checks slot availability via the Real-time Availability Tracker, reserves the chosen slot, and then updates the appointment schedules. A successful booking triggers notifications via the Notification System.
    """
    try:
        res = await project.bookAppointment_service.bookAppointment(
            userId, professionalId, scheduledTime
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )
