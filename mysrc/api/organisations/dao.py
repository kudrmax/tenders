from fastapi import HTTPException
from sqlalchemy import select

from mysrc.api.dao import DAO
from mysrc.api.organisations.models import MOrganization


class OrganizationCRUD(DAO):
    crud_model = MOrganization
    async def _get_organisation_by_id(self, organization_id: int) -> MOrganization:
        m_organization = await self.db.execute(select(MOrganization).where(MOrganization.id == organization_id))
        m_organization = m_organization.scalar_one_or_none()
        if not m_organization:
            raise HTTPException(status_code=404, detail=f"Organization with id={organization_id} not found.")
        return m_organization


