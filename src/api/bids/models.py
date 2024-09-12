import uuid
from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, func, TIMESTAMP, UUID

from src.database.database import Base


class BidStatus(str, Enum):
    created = "Created"
    published = "Published"
    closed = "Canceled"


class MBid(Base):
    __tablename__ = 'bid'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    tender_id = Column(UUID(as_uuid=True), ForeignKey('tender.id'), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey('organization.id'), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey('employee.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class MBidData(Base):
    __tablename__ = 'bid_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # id = Column(Integer, primary_key=True)
    bid_id = Column(UUID(as_uuid=True), ForeignKey('bind.id'), nullable=False)
    version = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
