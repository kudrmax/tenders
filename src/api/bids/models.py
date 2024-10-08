import uuid
from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, func, TIMESTAMP, UUID

from src.database.database import Base


class BidStatus(str, Enum):
    created = "Created"
    published = "Published"
    canceled = "Canceled"


class BidAuthorType(str, Enum):
    organization = "Organization"
    user = "User"


class BidDecision(str, Enum):
    approved = "Approved"
    rejected = "Rejected"


class MBid(Base):
    __tablename__ = 'bid'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(String, nullable=False)
    tender_id = Column(UUID(as_uuid=True), ForeignKey('tender.id'), nullable=False)
    author_type = Column(String, nullable=False)
    author_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class MBidData(Base):
    __tablename__ = 'bid_data'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bid_id = Column(UUID(as_uuid=True), ForeignKey('bid.id'), nullable=False)
    version = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)


class MBidFeedback(Base):
    __tablename__ = 'bid_feedback'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bid_id = Column(UUID(as_uuid=True), ForeignKey('bid.id'), nullable=False)
    feedback = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())


class MBidDecision(Base):
    __tablename__ = 'bid_decision'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bid_id = Column(UUID(as_uuid=True), ForeignKey('bid.id'), nullable=False)
    employee_id = Column(UUID(as_uuid=True), ForeignKey('employee.id'), nullable=False)
    decision = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
