from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, desc

from src.api.dao import DAO
from src.api.organisations.dao import OrganizationCRUD
from src.api.employees.dao import EmployeeCRUD
from src.api.tenders.models import TenderServiceType, TenderStatus, MTender, MTenderData
from src.api.tenders.schemas import STenderCreate, STenderRead, STenderUpdate


class TenderCRUD(DAO):
    async def _add_obj_to_obj_db(
            self, status: TenderStatus, organization_id: UUID, creator_id: UUID
    ) -> MTender:
        return await self._add_to_db(MTender(
            status=status,
            organization_id=organization_id,
            creator_id=creator_id,
        ))

    async def _add_obj_to_obj_data_db(
            self, tender_id: UUID, name: str, description: str, service_type: TenderServiceType, version: int, **kwargs
    ) -> MTenderData:
        return await self._add_to_db(MTenderData(
            tender_id=tender_id,
            name=name,
            description=description,
            service_type=service_type,
            version=version,
        ))

    async def _get_obj_by_id(self, tender_id: UUID) -> MTender:
        query = select(MTender).where(MTender.id == tender_id)
        m_tender = await self.db.execute(query)
        m_tender = m_tender.scalar_one_or_none()
        if not m_tender:
            raise HTTPException(status_code=404, detail=f"Tender with id={tender_id} not found")
        return m_tender

    async def _get_obj_data_with_last_version_by_id(self, tender_id: UUID) -> MTenderData:
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

    async def _get_obj_data_by_version(self, tender_id: UUID, version: int) -> MTenderData:
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
            tender_id: UUID | None = None,
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
            tender = await self._get_obj_by_id(tender_id)
        if not tender_data:
            tender_data = await self._get_obj_data_with_last_version_by_id(tender_id)
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
    async def create_tender(self, tender: STenderCreate) -> STenderRead:
        # проверка существования организации с id=tender.organizationId
        await self._get_organisation_by_id(organization_id=tender.organizationId)

        # проверка существования пользователя с username=tender.creatorUsername
        creator = await self._get_employee_by_username(username=tender.creatorUsername)

        # проверка что пользователь является ответственным за организацию
        if not await self.check_is_user_responsible(organization_id=tender.organizationId, user_id=creator.id):
            raise HTTPException(
                status_code=403,
                detail=f"User {creator.username} is not responsible for tender creation",
            )

        # добавление тендера в БД тендеров (MTender)
        m_tender = await self._add_obj_to_obj_db(
            status=TenderStatus.created,
            organization_id=tender.organizationId,
            creator_id=creator.id,
        )

        # добавление тендера в БД версий тендеров (MTenderData)
        m_tender_data = await self._add_obj_to_obj_data_db(
            tender_id=m_tender.id,
            name=tender.name,
            description=tender.description,
            service_type=tender.serviceType,
            version=1,
        )

        return await self.get_response_schema(tender=m_tender, tender_data=m_tender_data)

    async def update_tender_by_id(self, tender_id: UUID, tender_update_data: STenderUpdate, username: str):
        # проверка прав доступа
        await self.raise_exception_if_forbidden(username=username, tender_id=tender_id)

        # получение данных последней версии по тендеру
        m_tender_data_with_last_version = await self._get_obj_data_with_last_version_by_id(tender_id)

        # обновление данных тендера
        new_tender_data = {**m_tender_data_with_last_version.__dict__}
        for key, value in tender_update_data.model_dump(exclude_unset=True).items():
            new_tender_data[key] = value
        new_tender_data['version'] += 1

        # добавление новых данных в БД версий тендера
        m_new_tender_data = await self._add_obj_to_obj_data_db(**new_tender_data)

        return await self.get_response_schema(tender_id=tender_id, tender_data=m_new_tender_data)

    async def get_tenders_by_kwargs(self, **kwargs):
        service_type: TenderServiceType | None = kwargs.get('service_type', None)
        limit: int | None = kwargs.get('limit', None)
        offset: int | None = kwargs.get('offset', None)
        username: str | None = kwargs.get('username', None)

        query = select(MTender)
        m_tenders = await self.db.execute(query)
        m_tenders = m_tenders.scalars()

        tender_schemas = []
        for m_tender in m_tenders:
            m_tender_data = await self._get_obj_data_with_last_version_by_id(m_tender.id)

            # фильтер на service_type
            if service_type and m_tender_data.service_type != service_type:
                continue

            # фильтер на права доступа
            # показать тендер если пользователь ответственный за организацию или есть статус тендера == Published
            if username:
                is_responsible = await self.check_is_user_responsible(
                    organization_id=m_tender.organization_id,
                    user_id=(await self._get_employee_by_username(username=username)).id
                )
                tender_status = m_tender.status
                if not (is_responsible or tender_status == TenderStatus.published):
                    continue

            tender_schemas.append(
                await self.get_response_schema(tender=m_tender, tender_data=m_tender_data)
            )

        tender_schemas.sort(key=lambda x: x.name)
        return tender_schemas[offset:offset + limit]

    async def get_tender_status_by_id(self, tender_id: UUID, username: str):
        m_tender = await self._get_obj_by_id(tender_id)
        if m_tender.status == 'Published':
            return m_tender.status
        await self.raise_exception_if_forbidden(username=username, m_tender=m_tender)
        return m_tender.status

    async def change_tender_status_by_id(self, tender_id: UUID, status: TenderStatus, username: str):
        m_tender = await self._get_obj_by_id(tender_id)
        await self.raise_exception_if_forbidden(username=username, m_tender=m_tender)
        setattr(m_tender, 'status', status)
        await self.db.commit()
        return await self.get_response_schema(tender=m_tender)

    async def rollback_tender(self, tender_id: UUID, version: int, username: str):
        await self.raise_exception_if_forbidden(username=username, tender_id=tender_id)
        m_tender_data_with_given_version = await self._get_obj_data_by_version(tender_id, version)
        m_tender_data_with_last_version = await self._get_obj_data_with_last_version_by_id(tender_id)
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

    async def raise_exception_if_forbidden(
            self,
            username: str,
            tender_id: UUID | None = None,
            m_tender: MTender | None = None,
    ) -> None:
        """
        Проверка является ли пользователь с username=username ответственным за оргазинацию для тендера с id=tender_id
        """
        if not m_tender:
            if not tender_id:
                raise HTTPException(status_code=500, detail="One of tender_id, tender must be provided.")
            m_tender: MTender = await self._get_obj_by_id(tender_id=tender_id)
        organization_id = m_tender.organization_id

        m_employee = await self._get_employee_by_username(username=username)
        user_id = m_employee.id

        if not await self.check_is_user_responsible(organization_id=organization_id, user_id=user_id):
            raise HTTPException(
                status_code=403,
                detail=f'The user with {username=} does not have access to this operation.'
            )
