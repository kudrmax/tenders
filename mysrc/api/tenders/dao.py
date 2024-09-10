import asyncio

from fastapi import HTTPException
from sqlalchemy import select, func, desc

from mysrc.api.dao import DAO
from mysrc.api.tenders.models import MTender, MOrganization, MEmployee, MTenderVersion, TenderStatus, TenderServiceType
from mysrc.api.tenders.schemas import STenderCreate, STenderRead, STenderUpdate
from mysrc.api.dao_base import OldDAO
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
    ) -> MTenderVersion:
        m_tender_version = MTenderVersion(
            tender_id=tender_id,
            name=name,
            description=description,
            service_type=service_type,
            version=version,
        )
        self.db.add(m_tender_version)
        await self.db.commit()
        await self.db.refresh(m_tender_version)
        return m_tender_version

    async def _get_tender_by_id(self, tender_id: int) -> MTender:
        query = select(MTender).where(MTender.id == tender_id)
        m_tender = await self.db.execute(query)
        m_tender = m_tender.scalar_one_or_none()
        if not m_tender:
            raise HTTPException(status_code=404, detail=f"Tender with id={tender_id} not found")
        return m_tender

    async def _get_tender_data_with_last_version_by_id(self, tender_id: int) -> MTenderVersion:
        query = (
            select(MTenderVersion).
            where(MTenderVersion.tender_id == tender_id).
            order_by(desc(MTenderVersion.version)).
            limit(1)
        )
        tender_data_with_last_version = await self.db.execute(query)
        tender_data_with_last_version = tender_data_with_last_version.scalar_one_or_none()
        if not tender_data_with_last_version:
            raise HTTPException(status_code=404, detail=f"Tender data for tender with id={tender_id} not found.")
        return tender_data_with_last_version

    async def _get_tender_data_by_version(self, tender_id: int, version: int) -> MTenderVersion:
        query = (
            select(MTenderVersion).
            where(MTenderVersion.tender_id == tender_id).
            where(MTenderVersion.version == version)
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
            tender_data: MTenderVersion | None = None,
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


class TenderDAO(TenderCRUD):
    async def _check_auth(self, username: str):
        if False:
            raise HTTPException(status_code=402, detail="Недостаточно прав для выполнения действия.")
        return True

    async def create_tender(self, tender: STenderCreate):
        # проверка существования организации с id=tender.organizationId
        await self._get_organisation_by_id(organization_id=tender.organizationId)

        # проверка существования пользователя с username=tender.creatorUsername
        creator = await self._get_employee_by_username(username=tender.creatorUsername)

        # добавление тендера в БД тендеров
        m_tender = await self._add_tender_to_tender_db(
            status=tender.status,
            organization_id=tender.organizationId,
            creator_id=creator.id,
        )
        # добавление тендера в БД версий тендеров
        await self._add_tender_to_tender_data_db(
            tender_id=m_tender.id,
            name=tender.name,
            description=tender.description,
            service_type=tender.serviceType,
            version=1,
        )
        m_tender_version = await self._add_tender_to_tender_data_db(
            tender_id=m_tender.id,
            name=tender.name,
            description=tender.description,
            service_type=tender.serviceType,
            version=1,
        )

        return await self.get_response_schema(tender=m_tender, tender_data=m_tender_version)

    async def update_tender_by_id(self, tender_id: int, tender_update_data: STenderUpdate, username: str):
        # проверка прав доступа
        await self._check_auth(username=username)

        # получение данных последней версии по тендеру
        m_tender_last_version = await self._get_tender_data_with_last_version_by_id(tender_id)

        # обновление данных тендера
        new_tender_data = {**m_tender_last_version.__dict__}
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

        query = select(MTenderVersion)
        query = query.join(MTender, MTenderVersion.tender_id == MTender.id)
        query = query.add_columns(
            MTender.id,
            MTender.status,
            MTenderVersion.name,
            MTenderVersion.description,
            MTenderVersion.service_type,
            MTenderVersion.version,
            MTender.created_at,
        )

        if service_type:
            query = query.filter(MTenderVersion.service_type == service_type)
        if username:
            creator = await self._get_employee_by_username(username=username)
            query = query.filter(MTender.creator_id == creator.id)
        query = query.order_by(MTenderVersion.name)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        tenders = await self.db.execute(query)
        tenders = tenders.fetchall()
        print('========== TENDERS ==========')
        print(tenders)
        return [STenderRead(
            id=tender[1],
            status=tender[2],
            name=tender[3],
            description=tender[4],
            serviceType=tender[5],
            version=tender[6],
            createdAt=tender[7],
        ) for tender in tenders]

    # async def get_tender_last_version_value(self, tender_id: int) -> int:
    #     """
    #     SELECT mv.max_version
    #     FROM (
    #         SELECT tender_id, MAX(version) AS max_version
    #         FROM tender_version
    #         GROUP BY tender_id
    #     ) mv
    #     WHERE mv.tender_id == tender_id
    #     """
    #     subquery = (
    #         select(
    #             MTenderVersion.tender_id,
    #             func.max(MTenderVersion.version).label('max_version')
    #         )
    #         .group_by(MTenderVersion.tender_id)
    #         .subquery()
    #     )
    #     query = (
    #         select(subquery.c.max_version)
    #         .where(subquery.c.tender_id == tender_id)
    #     )
    #     result = await self.db.execute(query)
    #     max_version = result.scalar_one_or_none()
    #     return max_version

    # async def get_tender_last_version(self, tender_id: int) -> MTenderVersion:
    #     last_version = await self.get_tender_last_version_value(tender_id)
    #     return await self._get_tender_version_by_version(tender_id, last_version)

    # async def get_tender_last_version(self, tender_id: int):
    #     """
    #     # вариант 1
    #     SELECT *
    #     FROM tender t
    #     JOIN (
    #         SELECT tender_id, MAX(version) AS max_version
    #         FROM tender_version
    #         GROUP BY tender_id
    #     ) mv ON t.id = mv.tender_id
    #     JOIN tender_version tv ON t.id = tv.tender_id
    #     WHERE tv.version = mv.max_version;
    #
    #     # вариант 2
    #     SELECT t.*, tv.*
    #     FROM tender t
    #     JOIN (
    #         SELECT tender_id, MAX(version) AS max_version
    #         FROM tender_version
    #         GROUP BY tender_id
    #     ) mv ON t.id = mv.tender_id
    #     JOIN tender_version tv ON t.id = tv.tender_id AND tv.version = mv.max_version;
    #     """
    # sql_query = """
    # SELECT t.*, tv.*
    # FROM tender t
    # JOIN (
    #     SELECT tender_id, MAX(version) AS max_version
    #     FROM tender_version
    #     GROUP BY tender_id
    # ) mv ON t.id = mv.tender_id
    # JOIN tender_version tv ON t.id = tv.tender_id AND tv.version = mv.max_version;
    # """
    #
    # async with self.db as session:
    #     result = await session.execute(text(sql_query))
    #     rows = result.fetchall()
    #     return [TenderLastVersion(**dict(row)) for row in rows]
    # try:
    #     subquery = (
    #         select(MTenderVersion.tender_id, func.max(MTenderVersion.version).label('max_version'))
    #         .group_by(MTenderVersion.tender_id)
    #         .subquery()
    #     )
    #
    #     query = (
    #         select(MTender, MTenderVersion)
    #         .join(subquery, MTender.id == subquery.c.tender_id)
    #         .join(
    #             MTenderVersion,
    #             (MTender.id == MTenderVersion.tender_id) & (MTenderVersion.version == subquery.c.max_version)
    #         )
    #     )
    # except Exception as e:
    #     pass

    # async def get_latest_tender_versions_orm(self):
    #     try:
    #         # Подзапрос для нахождения максимальной версии для каждого тендера
    #         subquery = (
    #             select(MTenderVersion.tender_id, func.max(MTenderVersion.version).label('max_version'))
    #             .group_by(MTenderVersion.tender_id)
    #             .subquery()
    #         )
    #
    #         # Основной запрос с JOIN
    #         query = (
    #             select(MTender, MTenderVersion)
    #             .join(subquery, MTender.id == subquery.c.tender_id)
    #             .join(MTenderVersion,
    #                   (MTender.id == MTenderVersion.tender_id) & (MTenderVersion.version == subquery.c.max_version))
    #         )
    #
    #         result = await self.db.execute(query)
    #         tenders_with_latest_versions = result.all()
    #         return tenders_with_latest_versions
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

    async def get_tender_status_by_id(self, tender_id: int, username: str):
        m_tender = await self._get_tender_by_id(tender_id)
        return m_tender.status

    async def change_tender_status_by_id(self, tender_id: int, status: TenderStatus, username: str):
        if False:
            raise HTTPException(status_code=402, detail="Недостаточно прав для выполнения действия.")
        m_tender = await self._get_tender_by_id(tender_id)
        setattr(m_tender, 'status', status)
        await self.db.commit()
        return m_tender

    async def rollback_tender(self, tender_id: int, version: int, username: str):
        if False:
            raise HTTPException(status_code=402, detail="Недостаточно прав для выполнения действия.")
        m_tender_version = await self._get_tender_version_by_version(tender_id, version)
        last_version = await self.get_tender_last_version_value(tender_id)
        if not m_tender_version:
            raise HTTPException(status_code=404, detail='Tender version not found')
        m_new_tender_version = MTenderVersion(
            tender_id=tender_id,
            version=last_version + 1,
            name=m_tender_version.name,
            description=m_tender_version.description,
            service_type=m_tender_version.service_type,
        )
        self.db.add(m_new_tender_version)
        await self.db.commit()
        return m_new_tender_version


async def main():
    db = AsyncSessionLocal()
    tender_dao = TenderDAO(db=db)
    res = await tender_dao._get_tender_data_with_last_version(1)
    print(res)


if __name__ == '__main__':
    asyncio.run(main())
