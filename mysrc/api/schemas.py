from enum import Enum
from typing import Optional

from pydantic import BaseModel, UUID4

from mysrc.api.models import TenderServiceType


class ServiceType(str, Enum):
    construction = "Construction"


class Status(str, Enum):
    created = "Created"


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
    serviceType: ServiceType
    status: Status
    organizationId: int
    creatorUsername: str


class STenderLimitOffset(BaseModel):
    limit: int = 5
    offset: int = 0


class STenderFilter(STenderLimitOffset):
    service_type: Optional[TenderServiceType] = None
