from datetime import datetime

from pydantic import BaseModel

from src.api.bids.models import BindStatus


class SBindCreate(BaseModel):
    name: str
    description: str
    status: BindStatus
    tenderId: int
    organizationId: int
    creatorUsername: str


class SBindRead(BaseModel):
    id: int
    name: str
    description: str
    status: BindStatus
    version: int
    createdAt: datetime


class SBindUpdate(BaseModel):
    name: str | None = None
    description: str | None = None