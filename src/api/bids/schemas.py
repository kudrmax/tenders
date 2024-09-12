from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.api.bids.models import BidStatus


class SBindCreate(BaseModel):
    name: str
    description: str
    status: BidStatus
    tenderId: UUID
    organizationId: int
    creatorUsername: str


class SBindRead(BaseModel):
    id: UUID
    name: str
    description: str
    status: BidStatus
    version: int
    createdAt: datetime


class SBindUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
