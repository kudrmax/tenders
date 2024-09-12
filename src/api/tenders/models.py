from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func

from src.database import Base


class TenderServiceType(str, Enum):
    construction = "Construction"
    delivery = "Delivery"
    consulting = "Consulting"


class TenderStatus(str, Enum):
    created = "Created"
    published = "Published"
    closed = "Closed"


class MTender(Base):
    __tablename__ = 'tender'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('employee.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class MTenderData(Base):
    __tablename__ = 'tender_data'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    tender_id = Column(Integer, ForeignKey('tender.id'), nullable=False)
    version = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
