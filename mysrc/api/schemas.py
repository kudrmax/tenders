from enum import Enum

from pydantic import BaseModel, UUID4


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
