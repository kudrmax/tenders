from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select, desc

from src.api.bids.models import MBid, MBidData, BidStatus, BidAuthorType, MBidFeedback, BidDecision, MBidDecision
from src.api.bids.schemas import SBindCreate, SBindRead, SBindUpdate, SReviewRequest
from src.api.dao import DAO
from src.api.employees.dao import EmployeeCRUD
from src.api.employees.models import MEmployee
from src.api.organisations.dao import OrganizationCRUD
from src.api.organisations.models import MOrganizationResponsible
from src.api.tenders.models import MTender, TenderStatus


class BidCRUD(DAO):
    async def _add_obj_to_obj_db(
            self, status: BidStatus, tender_id, author_type: BidAuthorType, author_id: UUID
    ) -> MBid:
        return await self._add_to_db(MBid(
            status=status,
            tender_id=tender_id,
            author_type=author_type,
            author_id=author_id,
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

    async def get_tender_by_id(self, tender_id):
        m_tender = await self.db.execute(select(MTender).where(MTender.id == tender_id))
        m_tender = m_tender.scalar_one_or_none()
        if not m_tender:
            raise HTTPException(status_code=404, detail=f"Tender with id={tender_id} not found")
        return m_tender

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
            status=bid.status,
            authorType=bid.author_type,
            authorId=bid.author_id,
            version=bid_data.version,
            createdAt=bid.created_at,
        )


class BidDAO(BidCRUD, OrganizationCRUD, EmployeeCRUD):
    async def create_bid(self, bid: SBindCreate) -> SBindRead:
        if bid.authorType == BidAuthorType.organization:
            # проверка существования организации с id=bid.organizationId
            await self._get_organisation_by_id(organization_id=bid.authorId)
        elif bid.authorType == BidAuthorType.user:
            # проверка существования пользователя с id=bid.creatorUsername
            await self._get_employee_by_id(id=bid.authorId)
        else:
            raise HTTPException(
                status_code=400,
                detail=f'Unprocessable authorType "{bid.authorType}"',
            )

        # добавление тендера в БД тендеров
        m_bid = await self._add_obj_to_obj_db(
            status=BidStatus.created,
            tender_id=bid.tenderId,
            author_type=bid.authorType,
            author_id=bid.authorId,
        )
        # добавление тендера в БД версий тендеров
        m_bid_data = await self._add_obj_to_obj_data_db(
            bid_id=m_bid.id,
            name=bid.name,
            description=bid.description,
            version=1,
        )
        return await self.get_response_schema(bid=m_bid, bid_data=m_bid_data)

    async def update_bid_by_id(self, bid_id: UUID, bid_update_data: SBindUpdate, username: str):
        # проверка прав доступа
        await self.raise_exception_if_forbidden(username=username, bid_id=bid_id)

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

    async def get_bids_by_kwargs(self, **kwargs) -> List[SBindRead]:
        limit: int | None = kwargs.get('limit', 5)
        offset: int | None = kwargs.get('offset', 0)
        tender_id: UUID | None = kwargs.get('tender_id', None)
        username: str | None = kwargs.get('username', None)

        query = select(MBid)
        m_bids = await self.db.execute(query)
        m_bids = m_bids.scalars()

        if tender_id:
            await self.get_tender_by_id(tender_id=tender_id)

        bid_schemas = []
        for m_bid in m_bids:
            # фильтр на tender_id
            if tender_id and m_bid.tender_id != tender_id:
                continue

            # фильтер на username (права доступа)
            m_user = await self._get_employee_by_username(username=username)
            if username:
                add_flag = False
                if m_bid.status == BidStatus.published:  # разрешить, если статус 'Published'
                    add_flag = True
                elif await self.user_is_author(m_bid=m_bid, m_user=m_user):
                    add_flag = True
                elif await self.user_is_responsible(m_bid=m_bid, m_user=m_user):
                    add_flag = True
                if add_flag:
                    m_bid_data = await self._get_obj_data_with_last_version_by_id(m_bid.id)
                    bid_schemas.append(
                        await self.get_response_schema(bid=m_bid, bid_data=m_bid_data)
                    )

        bid_schemas.sort(key=lambda x: x.name)
        return bid_schemas[offset:offset + limit]

    async def user_is_author(self, m_bid: MBid, m_user: MEmployee) -> bool:
        if m_bid.author_type == BidAuthorType.user and m_bid.author_id == m_user.id:
            return True
        return False

    async def user_is_responsible(self, m_bid: MBid, m_user: MEmployee) -> bool:
        """
        @todo переделать
        если автором является организация, это не значит, что она может принимать решения
        """
        tender_id = m_bid.tender_id
        m_tender = await self.get_tender_by_id(tender_id)
        flag_by_tender = await self.check_is_user_responsible(
            user_id=m_user.id,
            organization_id=m_tender.organization_id
        )
        flag_by_type = False
        if m_bid.author_type == BidAuthorType.organization:
            flag_by_type = await self.check_is_user_responsible(
                user_id=m_user.id,
                organization_id=m_bid.author_id
            )
        return flag_by_type or flag_by_tender

    async def get_bid_status_by_id(self, bid_id: UUID, username: str):
        m_bid = await self._get_obj_by_id(bid_id)
        await self.raise_exception_if_forbidden(username=username, m_bid=m_bid)
        return m_bid.status

    async def change_bid_status_by_id(self, bid_id: UUID, status: BidStatus, username: str):
        m_bid = await self._get_obj_by_id(bid_id)
        await self.raise_exception_if_forbidden(username=username, m_bid=m_bid)
        setattr(m_bid, 'status', status)
        await self.db.commit()
        return await self.get_response_schema(
            bid=m_bid
        )

    async def rollback_bid(self, bid_id: UUID, version: int, username: str):
        await self.raise_exception_if_forbidden(username=username, bid_id=bid_id)
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
        return await self.get_response_schema(bid_data=m_new_bid_data, bid_id=bid_id)

    async def raise_exception_if_forbidden(
            self,
            username: str,
            bid_id: UUID | None = None,
            m_bid: MBid | None = None,
    ) -> None | bool:
        """
        Проверка является ли пользователь с username=username ответственным за оргазинацию для предложения с id=bid_id или является автором
        """
        if not m_bid:
            if not bid_id:
                raise HTTPException(status_code=500, detail="One of bid_id, tender must be provided.")
            m_bid: MBid = await self._get_obj_by_id(bid_id=bid_id)

        m_user = await self._get_employee_by_username(username=username)

        if await self.user_is_author(m_bid=m_bid, m_user=m_user):
            return True
        if await self.user_is_responsible(m_bid=m_bid, m_user=m_user):
            return True

        raise HTTPException(
            status_code=403,
            detail=f'The user with {username=} does not have access to this operation.'
        )

    async def add_feedback(self, bidId: UUID, bidFDeedback: str, username: str):
        m_bid = await self._get_obj_by_id(bid_id=bidId)
        m_user = await self._get_employee_by_username(username=username)
        if not await self.user_is_responsible(m_bid=m_bid, m_user=m_user):
            raise HTTPException(
                status_code=403,
                detail="You can't send feedback"
            )
        await self._add_to_db(MBidFeedback(
            bid_id=bidId,
            feedback=bidFDeedback
        ))
        return await self.get_response_schema(bid=m_bid)

    async def get_review(self, review_request: SReviewRequest):
        """
        Ответственный за организацию может посмотреть прошлые отзывы на предложения автора, который создал предложение для его тендера.
        """
        limit = review_request.limit
        offset = review_request.offset

        requester_username = review_request.requesterUsername
        author_username = review_request.authorUsername
        tender_id = review_request.tenderId

        m_requester = await self._get_employee_by_username(requester_username)
        m_author = await self._get_employee_by_username(author_username)
        m_tender = await self.get_tender_by_id(tender_id=tender_id)
        # m_bid = await self._get_obj_by_id(bid_id=bid_id)
        if not await self.check_is_user_responsible(
                user_id=m_requester.id,
                organization_id=m_tender.organization_id
        ):
            raise HTTPException(
                status_code=403,
                detail=f'The user with username={requester_username} does not have access to this operation.'
            )

        # проверить, что автор реально сделал предложение которое связано с тендером
        bids_connected_to_tender: List[SBindRead] = await self.get_bids_by_kwargs(
            username=requester_username,
            tender_id=tender_id
        )

        def check_is_author_create_bit_for_tender(bids_connected_to_tender: List[SBindRead], user_id: UUID):
            for bid in bids_connected_to_tender:
                if bid.authorType == BidAuthorType.user and bid.authorId == user_id:
                    return True
            return False

        if not check_is_author_create_bit_for_tender(bids_connected_to_tender, m_author.id):
            raise HTTPException(
                status_code=400,
                detail=f"User {author_username} did not create bids for tender with {tender_id=}"
            )
        # есть автор
        # он когда-то делал предложения
        # нахоим все его предложения
        # находим все отзывы на такие предложения
        query = (
            select(MBid).
            where(MBid.author_type == BidAuthorType.user).
            where(MBid.author_id == m_author.id)
        )
        feedbacks = []
        m_bids = await self.db.execute(query)
        m_bids = m_bids.scalars()
        for m_bid in m_bids:
            feedback = await self.db.execute(select(MBidFeedback).where(MBidFeedback.bid_id == m_bid.id))
            feedback = feedback.scalars()
            for f in feedback:
                if f:
                    feedbacks.append({
                        'id': f.id,
                        'description': f.feedback,
                        'createdAt': f.created_at,
                    })
        return feedbacks

    async def submit_decision(self, bidId: UUID, decision: BidDecision, username: str):
        m_bid = await self._get_obj_by_id(bid_id=bidId)
        m_user = await self._get_employee_by_username(username=username)
        is_responsible = await self.user_is_responsible(m_bid=m_bid, m_user=m_user)
        if not is_responsible:
            raise HTTPException(
                status_code=403,
                detail=f'The user with {username=} does not have access to this operation.'
            )
        # @todo проверить, чтобы один пользователь не могу добавить несколько раз одно и тоже
        await self._add_to_db(MBidDecision(
            bid_id=bidId,
            employee_id=m_user.id,
            decision=decision,
        ))
        await self.submit_decision_to_tender(bid_id=bidId)
        return await self.get_response_schema(bid=m_bid)

    async def submit_decision_to_tender(self, bid_id: UUID):
        m_bid = await self._get_obj_by_id(bid_id=bid_id)
        query = select(MBidDecision).where(MBidDecision.bid_id == bid_id)
        query_approved = query.where(MBidDecision.decision == BidDecision.approved)
        query_rejected = query.where(MBidDecision.decision == BidDecision.rejected)

        decisions_rejected = (await self.db.execute(query_rejected)).scalars().all()
        if len(decisions_rejected) > 0:
            m_bid.status = BidStatus.canceled
            await self.db.refresh(m_bid)
            await self.db.commit()
            return

        decisions_approved = (await self.db.execute(query_approved)).scalars().all()
        approved_counter = len(decisions_approved)

        tender_id = m_bid.tender_id
        m_tender = await self.get_tender_by_id(tender_id=tender_id)
        organization_id = m_tender.organization_id
        query_organisation = select(MOrganizationResponsible).where(
            MOrganizationResponsible.organization_id == organization_id)
        organisation_responsible_counter = len((await self.db.execute(query_organisation)).scalars().all())

        min_approved_count = min(3, organisation_responsible_counter)

        if approved_counter >= min_approved_count:
            m_tender.status = TenderStatus.closed
            await self.db.commit()
            return
