from fastapi import HTTPException
from sqlalchemy import select

from mysrc.api.models import MTender, MOrganizationResponsible, MOrganization, MEmployee, TenderServiceType, \
    MTenderVersion
from mysrc.api.schemas import STenderCreate, STenderRead
from mysrc.dao_base import DAO


class TenderDAO(DAO):

    async def create(self, tender: STenderCreate):
        # проверка существования организации с tender.organizationId
        organization = await self.db.execute(select(MOrganization).where(MOrganization.id == tender.organizationId))
        organization = organization.scalar_one_or_none()
        if not organization:
            raise HTTPException(status_code=404, detail="Организация не найдена.")

        # проверка существования пользователя с tender.creatorUsername
        creator = await self.db.execute(select(MEmployee).filter_by(username=tender.creatorUsername))
        creator = creator.scalar_one_or_none()
        if not creator:
            raise HTTPException(status_code=404, detail="Пользователь не найден.")

        # добавление тендера в БД
        try:
            m_tender = MTender(
                status=tender.status,
                organization_id=tender.organizationId,
                creator_id=creator.id,
            )
            self.db.add(m_tender)
            await self.db.commit()
            await self.db.refresh(m_tender)

            m_tender_version = MTenderVersion(
                tender_id=m_tender.id,
                name=tender.name,
                description=tender.description,
                service_type=tender.serviceType,
                version=1,
            )
            self.db.add(m_tender)
            await self.db.commit()
            await self.db.refresh(m_tender)
            return STenderRead(
                id=m_tender.id,
                name=m_tender_version.name,
                description=m_tender_version.description,
                status=m_tender.status,
                serviceType=m_tender_version.service_type,
                version=m_tender_version.version,
                createdAt=m_tender.created_at,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

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
