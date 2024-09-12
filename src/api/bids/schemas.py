from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.api.bids.models import BidStatus, BidAuthorType


class SBindCreate(BaseModel):
    name: str
    description: str
    tenderId: UUID
    authorType: BidAuthorType
    authorId: UUID


class SBindRead(BaseModel):
    id: UUID
    name: str
    status: BidStatus
    authorType: BidAuthorType
    authorId: UUID
    version: int
    createdAt: datetime


class SBindUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
