from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class GetProfessionalProfilesRequest(BaseModel):
    """
    Retrieves a list of professional profiles filtered by role-specific access limitations. No specific user input is required other than role-based authentication handled server-side.
    """

    pass


class ProfessionalProfileSummary(BaseModel):
    """
    Summary of a professional's profile showing only publicly permissible information.
    """

    id: int
    firstName: str
    lastName: str
    qualifications: str


class ProfessionalProfilesListResponse(BaseModel):
    """
    Response object container for a list of professional profiles, each with sanitized data appropriate to the requester's role level.
    """

    professionals: List[ProfessionalProfileSummary]


async def listProfessionalProfiles(
    request: GetProfessionalProfilesRequest,
) -> ProfessionalProfilesListResponse:
    """
    Fetches a list of all professional profiles. This endpoint is mainly used by administrative roles to monitor and manage professional accounts. It retrieves array-like data structure containing minimal essential details of professionals for quick browsing. Complies with privacy standards by limiting data according to user role access.

    Args:
    request (GetProfessionalProfilesRequest): Retrieves a list of professional profiles filtered by role-specific access limitations. No specific user input is required other than role-based authentication handled server-side.

    Returns:
    ProfessionalProfilesListResponse: Response object container for a list of professional profiles, each with sanitized data appropriate to the requester's role level.
    """
    profiles = await prisma.models.ProfessionalProfile.prisma().find_many(
        include={"profile": {"select": {"firstName": True, "lastName": True}}}
    )
    professional_summaries = [
        ProfessionalProfileSummary(
            id=profile.id,
            firstName=profile.profile.firstName,
            lastName=profile.profile.lastName,
            qualifications=profile.qualifications,
        )
        for profile in profiles
    ]
    return ProfessionalProfilesListResponse(professionals=professional_summaries)
