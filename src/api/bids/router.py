from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.api.bids.dao import BidDAO
from src.api.bids.models import BidStatus, BidDecision
from src.api.bids.schemas import SBindCreate, SBindUpdate, SReviewRequest

router = APIRouter(
    prefix="/api",
    tags=["Bids"],
)


@router.post("/bids/new")
async def create_bid(
        bid: SBindCreate,
        dao: BidDAO = Depends()
):
    return await dao.create_bid(bid)


@router.get("/bids/my")
async def get_bids_by_user(
        username: str,
        limit: int = Query(5, ge=0),
        offset: int = Query(0, ge=0),
        dao: BidDAO = Depends()
):
    return await dao.get_bids_by_kwargs(
        limit=limit,
        offset=offset,
        username=username
    )


@router.get("/bids/{tenderId}/list")
async def get_bids_by_tender_id(
        username: str,
        tenderId: UUID,
        limit: int = Query(5, ge=0),
        offset: int = Query(0, ge=0),
        dao: BidDAO = Depends()
):
    return await dao.get_bids_by_kwargs(
        limit=limit,
        offset=offset,
        username=username,
        tender_id=tenderId
    )


@router.get("/bids/{bidId}/status")
async def get_bid_status_by_id(
        bidId: UUID,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.get_bid_status_by_id(bidId, username)


@router.put("/bids/{bidId}/status")
async def change_bid_status_by_id(
        bidId: UUID,
        status: BidStatus,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.change_bid_status_by_id(bidId, status, username)


@router.patch("/bids/{bidId}/edit")
async def edit_bid(
        bidId: UUID,
        bid_update_data: SBindUpdate,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.update_bid_by_id(bidId, bid_update_data, username)


@router.put("/bids/{bidId}/rollback/{version}")
async def rollback_bid(
        bidId: UUID,
        version: int,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.rollback_bid(bidId, version, username)


@router.put("/bids/{bidId}/feedback")
async def add_feedback(
        bidId: UUID,
        bidFDeedback: str,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.add_feedback(bidId, bidFDeedback, username)


@router.get("/bids/{tenderId}/review")
async def get_review(
        tenderId: UUID,
        authorUsername: str,
        requesterUsername: str,
        limit: int = Query(5, ge=0),
        offset: int = Query(0, ge=0),
        dao: BidDAO = Depends()
):
    reviewRequest = SReviewRequest(
        tenderId=tenderId,
        authorUsername=authorUsername,
        requesterUsername=requesterUsername,
        limit=limit,
        offset=offset,
    )
    return await dao.get_review(reviewRequest)


@router.put("/bids/{bidId}/submit_decision")
async def submit_decision(
        bidId: UUID,
        decision: BidDecision,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.submit_decision(bidId, decision, username)
