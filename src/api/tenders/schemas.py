from datetime import datetime

from pydantic import BaseModel

from src.api.tenders.models import TenderServiceType, TenderStatus


class STenderCreate(BaseModel):
    name: str
    description: str
    serviceType: TenderServiceType
    status: TenderStatus
    organizationId: int
    creatorUsername: str


class STenderRead(BaseModel):
    id: int
    name: str
    description: str
    status: TenderStatus
    serviceType: TenderServiceType
    version: int
    createdAt: datetime


class STenderUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    serviceType: TenderServiceType | None = None
