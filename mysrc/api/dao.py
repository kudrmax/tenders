from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select, func

from mysrc.api.tenders.models import MTender, MOrganization, MEmployee, MTenderVersion, TenderStatus

from mysrc.database import get_db


class DAO:
    def __init__(self, db=Depends(get_db)):
        self.db: AsyncSession = db


class OrganizationCRUD(DAO):
    async def _get_organisation_by_id(self, organization_id: int) -> MOrganization:
        m_organization = await self.db.execute(select(MOrganization).where(MOrganization.id == organization_id))
        m_organization = m_organization.scalar_one_or_none()
        if not m_organization:
            raise HTTPException(status_code=404, detail=f"Organization with id={organization_id} not found.")
        return m_organization


class EmployeeCRUD(DAO):
    async def _get_employee_by_username(self, username: str) -> MEmployee:
        m_employee = await self.db.execute(select(MEmployee).filter_by(username=username))
        m_employee = m_employee.scalar_one_or_none()
        if not m_employee:
            raise HTTPException(status_code=404, detail=f"Employee with username {username} not found.")
        return m_employee
