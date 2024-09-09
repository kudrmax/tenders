from typing import List

from fastapi import HTTPException
from sqlalchemy import select, func, text

from mysrc.api.models import MTender, MOrganizationResponsible, MOrganization, MEmployee, TenderServiceType, \
    MTenderVersion, TenderStatus
from mysrc.api.schemas import STenderCreate, STenderRead, TenderLastVersionRead
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

    async def get_tender_last_version(self, tender_id: int):
        """
        SELECT mv.max_version
        FROM (
            SELECT tender_id, MAX(version) AS max_version
            FROM tender_version
            GROUP BY tender_id
        ) mv
        WHERE mv.tender_id == tender_id
        """
        subquery = (
            select(
                MTenderVersion.tender_id,
                func.max(MTenderVersion.version).label('max_version')
            )
            .group_by(MTenderVersion.tender_id)
            .subquery()
        )
        query = (
            select(subquery.c.max_version)
            .where(subquery.c.tender_id == tender_id)
        )
        result = await self.db.execute(query)
        max_version = result.scalar()
        return max_version

    async def get_tenders_by_kwargs(self, **kwargs):
        service_type = kwargs.get('service_type', None)
        limit = kwargs.get('limit', None)
        offset = kwargs.get('offset', None)
        username = kwargs.get('username', None)

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
            creator = await self.db.execute(select(MEmployee).where(MEmployee.username == username))
            creator = creator.scalar_one_or_none()
            if not creator:
                raise HTTPException(status_code=401, detail="Creator not found")
            query = query.filter(MTender.creator_id == creator.id)
        query = query.order_by(MTenderVersion.name)
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        tenders = await self.db.execute(query)
        tenders = tenders.fetchall()
        return [TenderLastVersionRead(
            tender_id=tender[1],
            status=tender[2],
            name=tender[3],
            description=tender[4],
            service_type=tender[5],
            version=tender[6],
            created_at=tender[7],
        ) for tender in tenders]

    async def _get_one_or_none_tender_by_id(self, tender_id: int):
        query = select(MTender).where(MTender.id == tender_id)
        m_tender = await self.db.execute(query)
        tender = m_tender.scalar_one_or_none()
        if not tender:
            raise HTTPException(status_code=404, detail="Tender not found")
        return tender

    async def get_tender_status_by_id(self, tender_id: int, username: str):
        m_tender = await self._get_one_or_none_tender_by_id(tender_id)
        return m_tender.status

    async def change_tender_status_by_id(self, tender_id: int, status: TenderStatus, username: str):
        m_tender = await self._get_one_or_none_tender_by_id(tender_id)
        if False:
            raise HTTPException(status_code=402, detail="Недостаточно прав для выполнения действия.")
        setattr(m_tender, 'status', status)
        await self.db.commit()
        return m_tender
