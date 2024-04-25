from datetime import datetime
from typing import List

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class AdminBookingsRequest(BaseModel):
    """
    This model is used for retrieving a comprehensive overview of all bookings. Access is restricted to administrators. No query parameters are necessary for this request.
    """

    pass


class UserBookingProfile(BaseModel):
    """
    Profile information pertinent to the booking, for quick reference by administrators.
    """

    userId: int
    email: str
    fullName: str


class ProfessionalBookingProfile(BaseModel):
    """
    Details about the professional relating to their qualifications and performance as viewed through reviews.
    """

    professionalId: int
    qualifications: str
    reviews: List[str]


class BookingDetail(BaseModel):
    """
    Structure detailing the various aspects of each booking, linking appointments to user and professional profiles.
    """

    appointmentId: int
    scheduledTime: datetime
    status: prisma.enums.AppointmentStatus
    userDetails: UserBookingProfile
    professionalDetails: ProfessionalBookingProfile


class AdminBookingsResponse(BaseModel):
    """
    Outputs detailed view of all appointments within the system, including linked user and professional profiles.
    """

    bookings: List[BookingDetail]


async def adminFetchAllBookings(request: AdminBookingsRequest) -> AdminBookingsResponse:
    """
    Exclusive to administrators, this endpoint provides a comprehensive overview of all bookings within the system. Useful for high-level management and troubleshooting scheduling conflicts or issues in the platform.

    Args:
        request (AdminBookingsRequest): This model is used for retrieving a comprehensive overview of all bookings. Access is restricted to administrators. No query parameters are necessary for this request.

    Returns:
        AdminBookingsResponse: Outputs detailed view of all appointments within the system, including linked user and professional profiles.
    """
    appointments = await prisma.models.Appointment.prisma().find_many(
        include={
            "user": {"include": {"profile": True}},
            "professional": {"include": {"profile": True, "reviews": True}},
        }
    )
    detailed_bookings = []
    for app in appointments:
        user_profile = app.user.profile
        user_booking_profile = UserBookingProfile(
            userId=app.user.id,
            email=app.user.email,
            fullName=user_profile.firstName + " " + user_profile.lastName,
        )
        prof_profile = app.professional.profile
        professional_booking_profile = ProfessionalBookingProfile(
            professionalId=app.professional.id,
            qualifications=app.professional.qualifications,
            reviews=[review.content for review in app.professional.reviews],
        )
        booking_detail = BookingDetail(
            appointmentId=app.id,
            scheduledTime=app.scheduledTime,
            status=app.status,
            userDetails=user_booking_profile,
            professionalDetails=professional_booking_profile,
        )
        detailed_bookings.append(booking_detail)
    response = AdminBookingsResponse(bookings=detailed_bookings)
    return response
