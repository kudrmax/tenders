from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, desc

from src.api.bids.models import MBid, MBidData, BidStatus
from src.api.bids.schemas import SBindCreate, SBindRead, SBindUpdate
from src.api.dao import DAO
from src.api.employees.dao import EmployeeCRUD
from src.api.organisations.dao import OrganizationCRUD


class BidCRUD(DAO):
    async def _add_obj_to_obj_db(
            self, status: BidStatus, tender_id, organization_id: int, creator_id: int
    ) -> MBid:
        return await self._add_to_db(MBid(
            status=status,
            tender_id=tender_id,
            organization_id=organization_id,
            creator_id=creator_id,
        ))

    async def _add_obj_to_obj_data_db(
            self, bid_id: UUID, name: str, description: str, version: int, **kwargs
    ) -> MBidData:
        return await self._add_to_db(MBidData(
            bid_id=bid_id,
            name=name,
            description=description,
            version=version,
        ))

    async def _get_obj_by_id(self, bid_id: UUID) -> MBid:
        query = select(MBid).where(MBid.id == bid_id)
        m_bid = await self.db.execute(query)
        m_bid = m_bid.scalar_one_or_none()
        if not m_bid:
            raise HTTPException(status_code=404, detail=f"Bind with id={bid_id} not found.")
        return m_bid

    async def _get_obj_data_with_last_version_by_id(self, bid_id: UUID) -> MBidData:
        query = (
            select(MBidData).
            where(MBidData.bid_id == bid_id).
            order_by(desc(MBidData.version)).
            limit(1)
        )
        m_bid_data_with_last_version = await self.db.execute(query)
        m_bid_data_with_last_version = m_bid_data_with_last_version.scalar_one_or_none()
        if not m_bid_data_with_last_version:
            raise HTTPException(status_code=404, detail=f"Bind data for bid with id={bid_id} not found.")
        return m_bid_data_with_last_version

    async def _get_obj_data_by_version(self, bid_id: UUID, version: int) -> MBidData:
        query = (
            select(MBidData).
            where(MBidData.bid_id == bid_id).
            where(MBidData.version == version)
        )
        m_bid_data = await self.db.execute(query)
        m_bid_data = m_bid_data.scalar_one_or_none()
        if not m_bid_data:
            raise HTTPException(
                status_code=404,
                detail=f"Bind data with version={version} for bid with id={bid_id} not found."
            )
        return m_bid_data

    async def get_response_schema(
            self,
            bid_id: UUID | None = None,
            bid: MBid | None = None,
            bid_data: MBidData | None = None,
    ) -> SBindRead:
        if not bid_id:
            if bid:
                bid_id = bid.id
            elif bid_data:
                bid_id = bid_data.bid_id
            else:
                raise HTTPException(status_code=500, detail="One of bid_id, bid, bid_data must be provided")

        if not bid:
            bid: MBid = await self._get_obj_by_id(bid_id)
        if not bid_data:
            bid_data: MBidData = await self._get_obj_data_with_last_version_by_id(bid_id)
        return SBindRead(
            id=bid.id,
            name=bid_data.name,
            description=bid_data.description,
            status=bid.status,
            version=bid_data.version,
            createdAt=bid.created_at,
        )


class BidDAO(BidCRUD, OrganizationCRUD, EmployeeCRUD):
    async def create_bid(self, bid: SBindCreate) -> SBindRead:
        # проверка существования организации с id=bid.organizationId
        await self._get_organisation_by_id(organization_id=bid.organizationId)

        # проверка существования пользователя с username=bid.creatorUsername
        creator = await self._get_employee_by_username(username=bid.creatorUsername)

        # добавление тендера в БД тендеров
        m_bid = await self._add_obj_to_obj_db(
            status=bid.status,
            tender_id=bid.tenderId,
            organization_id=bid.organizationId,
            creator_id=creator.id,
        )
        # добавление тендера в БД версий тендеров
        m_bid_data = await self._add_obj_to_obj_data_db(
            bid_id=m_bid.id,
            name=bid.name,
            description=bid.description,
            service_type=bid.serviceType,
            version=1,
        )
        return await self.get_response_schema(bid=m_bid, bid_data=m_bid_data)

    async def update_bid_by_id(self, bid_id: UUID, bid_update_data: SBindUpdate, username: str):
        # проверка прав доступа
        # await self._check_auth(username=username)

        # получение данных последней версии по предложению
        m_bid_data_with_last_version = await self._get_obj_data_with_last_version_by_id(bid_id)

        # обновление данных предложения
        new_bid_data = {**m_bid_data_with_last_version.__dict__}
        for key, value in bid_update_data.model_dump(exclude_unset=True).items():
            new_bid_data[key] = value
        new_bid_data['version'] += 1

        # добавление новых данных в БД данных предложений
        m_new_bid_data = await self._add_obj_to_obj_data_db(**new_bid_data)

        return await self.get_response_schema(bid_id=bid_id, bid_data=m_new_bid_data)

    async def get_bids_by_kwargs(self, **kwargs):
        limit: int | None = kwargs.get('limit', None)
        offset: int | None = kwargs.get('offset', None)
        tender_id: int | None = kwargs.get('tender_id', None)
        username: str | None = kwargs.get('username', None)

        query = select(MBid)
        if username:
            creator = await self._get_employee_by_username(username=username)
            query = query.filter(MBid.creator_id == creator.id)
        m_bids = await self.db.execute(query)
        m_bids = m_bids.scalars()

        bid_schemas = []
        for m_bid in m_bids:
            if tender_id and m_bid.tender_id != tender_id:
                continue
            m_bid_data = await self._get_obj_data_with_last_version_by_id(m_bid.id)
            bid_schemas.append(await self.get_response_schema(bid=m_bid, bid_data=m_bid_data))

        bid_schemas.sort(key=lambda x: x.name)
        return bid_schemas[offset:offset + limit]

    async def get_bid_status_by_id(self, bid_id: UUID, username: str):
        m_bid = await self._get_obj_by_id(bid_id)
        return m_bid.status

    async def change_bid_status_by_id(self, bid_id: UUID, status: BidStatus, username: str):
        m_bid = await self._get_obj_by_id(bid_id)
        setattr(m_bid, 'status', status)
        await self.db.commit()
        return m_bid

    async def rollback_bid(self, bid_id: UUID, version: int, username: str):
        m_bid_data_with_given_version = await self._get_obj_data_by_version(bid_id, version)
        m_bid_data_with_last_version = await self._get_obj_data_with_last_version_by_id(bid_id)
        m_new_bid_data = MBidData(
            bid_id=bid_id,
            version=m_bid_data_with_last_version.version + 1,
            name=m_bid_data_with_given_version.name,
            description=m_bid_data_with_given_version.description,
        )
        self.db.add(m_new_bid_data)
        await self.db.commit()
        return m_new_bid_data