from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select

from src.api.dao import DAO
from src.api.organisations.models import MOrganization, MOrganizationResponsible


class OrganizationCRUD(DAO):
    crud_model = MOrganization

    async def _get_organisation_by_id(self, organization_id: UUID) -> MOrganization:
        m_organization = await self.db.execute(select(MOrganization).where(MOrganization.id == organization_id))
        m_organization = m_organization.scalar_one_or_none()
        if not m_organization:
            raise HTTPException(status_code=404, detail=f"Organization with id={organization_id} not found.")
        return m_organization

    async def check_is_user_responsible(self, organization_id: UUID, user_id: UUID) -> bool:
        query = (
            select(MOrganizationResponsible).
            where(MOrganizationResponsible.organization_id == organization_id).
            where(MOrganizationResponsible.user_id == user_id)
        )
        if not (await self.db.execute(query)).scalar_one_or_none():
            return False
        return True
