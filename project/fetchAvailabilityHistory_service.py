from datetime import datetime
from typing import List

import prisma
import prisma.models
from pydantic import BaseModel


class AvailabilityRecord(BaseModel):
    """
    A record detailing an update to a professional's availability status, including the timestamp of the change.
    """

    datetime: datetime
    isAvailable: bool


class AvailabilityHistoryResponse(BaseModel):
    """
    Response model containing the history of availability status changes for a given professional. Each entry includes timestamps and availability states.
    """

    history: List[AvailabilityRecord]


async def fetchAvailabilityHistory(professionalId: int) -> AvailabilityHistoryResponse:
    """
    Fetches the history of availability status changes for a specific professional. This route helps in auditing and tracking the status changes over time. It pulls data from a historical database where past statuses are logged. The response includes time-stamped records of availability updates.

    Args:
    professionalId (int): The unique identifier of the professional whose availability history is to be retrieved.

    Returns:
    AvailabilityHistoryResponse: Response model containing the history of availability status changes for a given professional. Each entry includes timestamps and availability states.

    Example:
        fetchAvailabilityHistory(123)
        > Returns AvailabilityHistoryResponse containing list of AvailabilityRecord of changes in availability.
    """
    history_records = await prisma.models.Availability.prisma().find_many(
        where={"professionalId": professionalId}, order={"datetime": "asc"}
    )
    history = [
        AvailabilityRecord(datetime=record.datetime, isAvailable=record.isAvailable)
        for record in history_records
    ]
    return AvailabilityHistoryResponse(history=history)
