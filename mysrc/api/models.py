import uuid
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Text, TIMESTAMP, func, UUID
)
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from sqlalchemy.orm import relationship

from mysrc.database import Base

organization_type_enum = PG_ENUM('IE', 'LLC', 'JSC', name='organization_type', create_type=False)


class MEmployee(Base):
    """
    Модель для работы со таблицей, которая создается так:
    CREATE TABLE employee (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    __tablename__ = 'employee'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # organizations = relationship('OrganizationResponsible', back_populates='employee')


class MOrganization(Base):
    """
    Модель для работы со таблицей, которая создается так:
    CREATE TABLE organization (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        type organization_type,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    __tablename__ = 'organization'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type = Column(organization_type_enum)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # responsibles = relationship('OrganizationResponsible', back_populates='organization')


class MOrganizationResponsible(Base):
    """
    Модель для работы со таблицей, которая создается так:
    CREATE TABLE organization_responsible (
        id SERIAL PRIMARY KEY,
        organization_id INT REFERENCES organization(id) ON DELETE CASCADE,
        user_id INT REFERENCES employee(id) ON DELETE CASCADE
    );
    """
    __tablename__ = 'organization_responsible'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organization.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('employee.id', ondelete='CASCADE'))

    # organization = relationship('Organization', back_populates='responsibles')
    # employee = relationship('Employee', back_populates='organizations')


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


class MTenderVersion(Base):
    __tablename__ = 'tender_version'

    # id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id = Column(Integer, primary_key=True)
    tender_id = Column(Integer, ForeignKey('tender.id'), nullable=False)
    version = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    service_type = Column(String, nullable=False)
