from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, UUID4

from mysrc.api.models import TenderServiceType, TenderStatus


class STenderCreate(BaseModel):
    """
    {
      "name": "string",
      "description": "string",
      "serviceType": "Construction",
      "status": "Created",
      "organizationId": "550e8400-e29b-41d4-a716-446655440000",
      "creatorUsername": "test_user"
    }
    """
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


class TenderLastVersionRead(BaseModel):
    tender_id: int
    status: TenderStatus
    name: str
    description: str
    service_type: TenderServiceType
    version: int
    created_at: datetime
