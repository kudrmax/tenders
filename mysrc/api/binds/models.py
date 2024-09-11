from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey, func, TIMESTAMP

from mysrc.database import Base


class BindStatus(str, Enum):
    created = "Created"
    published = "Published"
    closed = "Canceled"


class MBind(Base):
    __tablename__ = 'bind'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    tender_id = Column(Integer, ForeignKey('tender.id'), nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'), nullable=False)
    creator_id = Column(Integer, ForeignKey('employee.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class MBindData(Base):
    __tablename__ = 'bind_data'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    bind_id = Column(Integer, ForeignKey('bind.id'), nullable=False)
    version = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
