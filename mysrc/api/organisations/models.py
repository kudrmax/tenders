from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func, ForeignKey

from mysrc.database import Base

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

organization_type_enum = PG_ENUM('IE', 'LLC', 'JSC', name='organization_type', create_type=False)


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
