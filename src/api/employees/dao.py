from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select

from src.api.dao import DAO
from src.api.employees.models import MEmployee


class EmployeeCRUD(DAO):
    crud_model = MEmployee

    async def _get_employee_by_username(self, username: str) -> MEmployee:
        m_employee = await self.db.execute(select(MEmployee).filter_by(username=username))
        m_employee = m_employee.scalar_one_or_none()
        if not m_employee:
            raise HTTPException(status_code=404, detail=f"Employee with username {username} not found.")
        return m_employee

    async def _get_employee_by_id(self, id: UUID) -> MEmployee:
        m_employee = await self.db.execute(select(MEmployee).filter_by(id=id))
        m_employee = m_employee.scalar_one_or_none()
        if not m_employee:
            raise HTTPException(status_code=404, detail=f"Employee with id={id} not found.")
        return m_employee
