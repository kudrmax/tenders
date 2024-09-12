from fastapi import HTTPException
from sqlalchemy import select, desc

from src.api.bids.models import MBind, MBindData, BindStatus
from src.api.bids.schemas import SBindCreate, SBindRead, SBindUpdate
from src.api.dao import DAO
from src.api.employees.dao import EmployeeCRUD
from src.api.organisations.dao import OrganizationCRUD


class BindCRUD(DAO):
    async def _add_obj_to_obj_db(
            self, status: BindStatus, tender_id, organization_id: int, creator_id: int
    ) -> MBind:
        return await self._add_to_db(MBind(
            status=status,
            tender_id=tender_id,
            organization_id=organization_id,
            creator_id=creator_id,
        ))

    async def _add_obj_to_obj_data_db(
            self, bind_id: int, name: str, description: str, version: int, **kwargs
    ) -> MBindData:
        return await self._add_to_db(MBindData(
            bind_id=bind_id,
            name=name,
            description=description,
            version=version,
        ))

    async def _get_obj_by_id(self, bind_id: int) -> MBind:
        query = select(MBind).where(MBind.id == bind_id)
        m_bind = await self.db.execute(query)
        m_bind = m_bind.scalar_one_or_none()
        if not m_bind:
            raise HTTPException(status_code=404, detail=f"Bind with id={bind_id} not found.")
        return m_bind

    async def _get_obj_data_with_last_version_by_id(self, bind_id: int) -> MBindData:
        query = (
            select(MBindData).
            where(MBindData.bind_id == bind_id).
            order_by(desc(MBindData.version)).
            limit(1)
        )
        m_bind_data_with_last_version = await self.db.execute(query)
        m_bind_data_with_last_version = m_bind_data_with_last_version.scalar_one_or_none()
        if not m_bind_data_with_last_version:
            raise HTTPException(status_code=404, detail=f"Bind data for bind with id={bind_id} not found.")
        return m_bind_data_with_last_version

    async def _get_obj_data_by_version(self, bind_id: int, version: int) -> MBindData:
        query = (
            select(MBindData).
            where(MBindData.bind_id == bind_id).
            where(MBindData.version == version)
        )
        m_bind_data = await self.db.execute(query)
        m_bind_data = m_bind_data.scalar_one_or_none()
        if not m_bind_data:
            raise HTTPException(
                status_code=404,
                detail=f"Bind data with version={version} for bind with id={bind_id} not found."
            )
        return m_bind_data

    async def get_response_schema(
            self,
            bind_id: int | None = None,
            bind: MBind | None = None,
            bind_data: MBindData | None = None,
    ) -> SBindRead:
        if not bind_id:
            if bind:
                bind_id = bind.id
            elif bind_data:
                bind_id = bind_data.bind_id
            else:
                raise HTTPException(status_code=500, detail="One of bind_id, bind, bind_data must be provided")

        if not bind:
            bind: MBind = await self._get_obj_by_id(bind_id)
        if not bind_data:
            bind_data: MBindData = await self._get_obj_data_with_last_version_by_id(bind_id)
        return SBindRead(
            id=bind.id,
            name=bind_data.name,
            description=bind_data.description,
            status=bind.status,
            version=bind_data.version,
            createdAt=bind.created_at,
        )


class BindDAO(BindCRUD, OrganizationCRUD, EmployeeCRUD):
    async def create_bind(self, bind: SBindCreate) -> SBindRead:
        # проверка существования организации с id=bind.organizationId
        await self._get_organisation_by_id(organization_id=bind.organizationId)

        # проверка существования пользователя с username=bind.creatorUsername
        creator = await self._get_employee_by_username(username=bind.creatorUsername)

        # добавление тендера в БД тендеров
        m_bind = await self._add_obj_to_obj_db(
            status=bind.status,
            tender_id=bind.tenderId,
            organization_id=bind.organizationId,
            creator_id=creator.id,
        )
        # добавление тендера в БД версий тендеров
        m_bind_data = await self._add_obj_to_obj_data_db(
            bind_id=m_bind.id,
            name=bind.name,
            description=bind.description,
            service_type=bind.serviceType,
            version=1,
        )
        return await self.get_response_schema(bind=m_bind, bind_data=m_bind_data)

    async def update_bind_by_id(self, bind_id: int, bind_update_data: SBindUpdate, username: str):
        # проверка прав доступа
        # await self._check_auth(username=username)

        # получение данных последней версии по предложению
        m_bind_data_with_last_version = await self._get_obj_data_with_last_version_by_id(bind_id)

        # обновление данных предложения
        new_bind_data = {**m_bind_data_with_last_version.__dict__}
        for key, value in bind_update_data.model_dump(exclude_unset=True).items():
            new_bind_data[key] = value
        new_bind_data['version'] += 1

        # добавление новых данных в БД данных предложений
        m_new_bind_data = await self._add_obj_to_obj_data_db(**new_bind_data)

        return await self.get_response_schema(bind_id=bind_id, bind_data=m_new_bind_data)

    async def get_binds_by_kwargs(self, **kwargs):
        limit: int | None = kwargs.get('limit', None)
        offset: int | None = kwargs.get('offset', None)
        tender_id: int | None = kwargs.get('tender_id', None)
        username: str | None = kwargs.get('username', None)

        query = select(MBind)
        if username:
            creator = await self._get_employee_by_username(username=username)
            query = query.filter(MBind.creator_id == creator.id)
        m_binds = await self.db.execute(query)
        m_binds = m_binds.scalars()

        bind_schemas = []
        for m_bind in m_binds:
            if tender_id and m_bind.tender_id != tender_id:
                continue
            m_bind_data = await self._get_obj_data_with_last_version_by_id(m_bind.id)
            bind_schemas.append(await self.get_response_schema(bind=m_bind, bind_data=m_bind_data))

        bind_schemas.sort(key=lambda x: x.name)
        return bind_schemas[offset:offset + limit]

    async def get_bind_status_by_id(self, bind_id: int, username: str):
        m_bind = await self._get_obj_by_id(bind_id)
        return m_bind.status

    async def change_bind_status_by_id(self, bind_id: int, status: BindStatus, username: str):
        m_bind = await self._get_obj_by_id(bind_id)
        setattr(m_bind, 'status', status)
        await self.db.commit()
        return m_bind

    async def rollback_bind(self, bind_id: int, version: int, username: str):
        m_bind_data_with_given_version = await self._get_obj_data_by_version(bind_id, version)
        m_bind_data_with_last_version = await self._get_obj_data_with_last_version_by_id(bind_id)
        m_new_bind_data = MBindData(
            bind_id=bind_id,
            version=m_bind_data_with_last_version.version + 1,
            name=m_bind_data_with_given_version.name,
            description=m_bind_data_with_given_version.description,
        )
        self.db.add(m_new_bind_data)
        await self.db.commit()
        return m_new_bind_data