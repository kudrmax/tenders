import asyncio

from fastapi import HTTPException
from sqlalchemy import select, desc

from mysrc.api.dao import DAO
from mysrc.api.organisations.dao import OrganizationCRUD
from mysrc.api.employees.dao import EmployeeCRUD
from mysrc.api.tenders.models import TenderServiceType, TenderStatus, MTender, MTenderData
from mysrc.api.tenders.schemas import STenderCreate, STenderRead, STenderUpdate
from mysrc.database import AsyncSessionLocal


class TenderCRUD(DAO):
    async def _add_tender_to_tender_db(
            self, status: TenderStatus, organization_id: int, creator_id: int
    ) -> MTender:
        m_tender = MTender(
            status=status,
            organization_id=organization_id,
            creator_id=creator_id,
        )
        self.db.add(m_tender)
        await self.db.commit()
        await self.db.refresh(m_tender)
        return m_tender

    async def _add_tender_to_tender_data_db(
            self, tender_id: int, name: str, description: str, service_type: TenderServiceType, version: int, **kwargs
    ) -> MTenderData:
        m_tender_data = MTenderData(
            tender_id=tender_id,
            name=name,
            description=description,
            service_type=service_type,
            version=version,
        )
        self.db.add(m_tender_data)
        await self.db.commit()
        await self.db.refresh(m_tender_data)
        return m_tender_data

    async def _get_tender_by_id(self, tender_id: int) -> MTender:
        query = select(MTender).where(MTender.id == tender_id)
        m_tender = await self.db.execute(query)
        m_tender = m_tender.scalar_one_or_none()
        if not m_tender:
            raise HTTPException(status_code=404, detail=f"Tender with id={tender_id} not found")
        return m_tender

    async def _get_tender_data_with_last_version_by_id(self, tender_id: int) -> MTenderData:
        query = (
            select(MTenderData).
            where(MTenderData.tender_id == tender_id).
            order_by(desc(MTenderData.version)).
            limit(1)
        )
        m_tender_data_with_last_version = await self.db.execute(query)
        m_tender_data_with_last_version = m_tender_data_with_last_version.scalar_one_or_none()
        if not m_tender_data_with_last_version:
            raise HTTPException(status_code=404, detail=f"Tender data for tender with id={tender_id} not found.")
        return m_tender_data_with_last_version

    async def _get_tender_data_by_version(self, tender_id: int, version: int) -> MTenderData:
        query = (
            select(MTenderData).
            where(MTenderData.tender_id == tender_id).
            where(MTenderData.version == version)
        )
        m_tender_data = await self.db.execute(query)
        m_tender_data = m_tender_data.scalar_one_or_none()
        if not m_tender_data:
            raise HTTPException(
                status_code=404,
                detail=f"Tender data with version={version} for tender with id={tender_id} not found."
            )
        return m_tender_data

    async def get_response_schema(
            self,
            tender_id: int | None = None,
            tender: MTender | None = None,
            tender_data: MTenderData | None = None,
    ) -> STenderRead:
        if not tender_id:
            if tender:
                tender_id = tender.id
            elif tender_data:
                tender_id = tender_data.tender_id
            else:
                raise HTTPException(status_code=500, detail="One of tender_id, tender, tender_data must be provided")

        if not tender:
            tender = await self._get_tender_by_id(tender_id)
        if not tender_data:
            tender_data = await self._get_tender_data_with_last_version_by_id(tender_id)
        print()
        return STenderRead(
            id=tender.id,
            name=tender_data.name,
            description=tender_data.description,
            status=tender.status,
            serviceType=tender_data.service_type,
            version=tender_data.version,
            createdAt=tender.created_at,
        )


class TenderDAO(TenderCRUD, OrganizationCRUD, EmployeeCRUD):
    async def _check_auth(self, username: str):
        if False:
            raise HTTPException(status_code=402, detail="Недостаточно прав для выполнения действия.")
        return True

    async def create_tender(self, tender: STenderCreate) -> STenderRead:
        # проверка существования организации с id=tender.organizationId
        await self._get_organisation_by_id(organization_id=tender.organizationId)

        # проверка существования пользователя с username=tender.creatorUsername
        creator = await self._get_employee_by_username(username=tender.creatorUsername)

        # добавление тендера в БД тендеров (MTender)
        m_tender = await self._add_tender_to_tender_db(
            status=tender.status,
            organization_id=tender.organizationId,
            creator_id=creator.id,
        )

        # добавление тендера в БД версий тендеров (MTenderData)
        m_tender_data = await self._add_tender_to_tender_data_db(
            tender_id=m_tender.id,
            name=tender.name,
            description=tender.description,
            service_type=tender.serviceType,
            version=1,
        )

        return await self.get_response_schema(tender=m_tender, tender_data=m_tender_data)

    async def update_tender_by_id(self, tender_id: int, tender_update_data: STenderUpdate, username: str):
        # проверка прав доступа
        await self._check_auth(username=username)

        # получение данных последней версии по тендеру
        m_tender_data_with_last_version = await self._get_tender_data_with_last_version_by_id(tender_id)

        # обновление данных тендера
        new_tender_data = {**m_tender_data_with_last_version.__dict__}
        for key, value in tender_update_data.model_dump(exclude_unset=True).items():
            new_tender_data[key] = value
        new_tender_data['version'] += 1

        # добавление новых данных в БД версий тендера
        m_new_tender_data = await self._add_tender_to_tender_data_db(**new_tender_data)

        return await self.get_response_schema(tender_id=tender_id, tender_data=m_new_tender_data)

    async def get_tenders_by_kwargs(self, **kwargs):
        service_type: TenderServiceType | None = kwargs.get('service_type', None)
        limit: int | None = kwargs.get('limit', None)
        offset: int | None = kwargs.get('offset', None)
        username: str | None = kwargs.get('username', None)

        query = select(MTender)
        if username:
            creator = await self._get_employee_by_username(username=username)
            query = query.filter(MTender.creator_id == creator.id)
        m_tenders = await self.db.execute(query)
        m_tenders = m_tenders.scalars()

        tender_schemas = []
        for m_tender in m_tenders:
            m_tender_data = await self._get_tender_data_with_last_version_by_id(m_tender.id)
            if not service_type or (service_type and m_tender_data.service_type == service_type):
                tender_schemas.append(await self.get_response_schema(tender=m_tender, tender_data=m_tender_data))

        tender_schemas.sort(key=lambda x: x.name)
        return tender_schemas[offset:offset + limit]

    async def get_tender_status_by_id(self, tender_id: int, username: str):
        m_tender = await self._get_tender_by_id(tender_id)
        return m_tender.status

    async def change_tender_status_by_id(self, tender_id: int, status: TenderStatus, username: str):
        m_tender = await self._get_tender_by_id(tender_id)
        setattr(m_tender, 'status', status)
        await self.db.commit()
        return m_tender

    async def rollback_tender(self, tender_id: int, version: int, username: str):
        m_tender_data_with_given_version = await self._get_tender_data_by_version(tender_id, version)
        m_tender_data_with_last_version = await self._get_tender_data_with_last_version_by_id(tender_id)
        m_new_tender_data = MTenderData(
            tender_id=tender_id,
            version=m_tender_data_with_last_version.version + 1,
            name=m_tender_data_with_given_version.name,
            description=m_tender_data_with_given_version.description,
            service_type=m_tender_data_with_given_version.service_type,
        )
        self.db.add(m_new_tender_data)
        await self.db.commit()
        return m_new_tender_data
