from fastapi import HTTPException
from sqlalchemy import select

from mysrc.api.models import MTender, MOrganizationResponsible, MOrganization, MEmployee, TenderServiceType
from mysrc.api.schemas import STenderCreate, Status, STenderFilter
from mysrc.dao_base import DAO


class TenderDAO(DAO):

    async def create(self, tender: STenderCreate):
        """
        {
          "name": "string",
          "description": "string",
          "serviceType": "Construction",
          "status": "Created",
          "organizationId": "550e8400-e29b-41d4-a716-446655440000",
          "creatorUsername": "test_user"
        }
        """
        # проверка существования организации
        organization = await self.db.execute(select(MOrganization).where(MOrganization.id == tender.organizationId))
        organization = organization.scalar_one_or_none()
        if not organization:
            raise HTTPException(status_code=404, detail="Organization not found")

        # поиск creator_id по username
        creator = await self.db.execute(select(MEmployee).filter_by(username=tender.creatorUsername))
        creator = creator.scalar_one_or_none()
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")

        # добавление в БД
        m_tender = MTender(
            name=tender.name,
            description=tender.description,
            service_type=tender.serviceType,
            status=tender.status,
            organization_id=tender.organizationId,
            creator_id=creator.id,
        )
        self.db.add(m_tender)
        await self.db.commit()
        await self.db.refresh(m_tender)

        return m_tender

    async def get_tenders_by_kwargs(self, **kwargs):
        try:
            service_type = kwargs.get('service_type', None)
            limit = kwargs.get('limit', None)
            offset = kwargs.get('offset', None)
            username = kwargs.get('username', None)

            query = select(MTender).order_by(MTender.name)
            if service_type:
                query = query.filter(MTender.service_type == service_type)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            if username:
                creator = await self.db.execute(select(MEmployee).where(MEmployee.username == username))
                creator = creator.scalar_one_or_none()
                if not creator:
                    raise HTTPException(status_code=404, detail="Creator not found")
                query = query.filter(MTender.creator_id == creator.id)

            result = await self.db.execute(query)
            tenders = result.scalars().all()
            return tenders
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
