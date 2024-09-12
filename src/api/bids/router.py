from fastapi import APIRouter, Depends

from src.api.bids.dao import BidDAO
from src.api.bids.models import BidStatus
from src.api.bids.schemas import SBindCreate, SBindUpdate

router = APIRouter(
    prefix="/api",
    tags=["Bids"],
)


@router.post("/bids/new")
async def create_bid(
        tender: SBindCreate,
        dao: BidDAO = Depends()
):
    return await dao.create_bid(tender)


@router.get("/bids/my")
async def get_tenders_by_user(
        username: str,
        limit: int = 5,
        offset: int = 0,
        dao: BidDAO = Depends()
):
    return await dao.get_bids_by_kwargs(
        limit=limit,
        offset=offset,
        username=username
    )


@router.get("/bids/{tenderId}/list")
async def get_tenders_by_user(
        username: str,
        tenderId: int,
        limit: int = 5,
        offset: int = 0,
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
        bidId: int,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.get_bid_status_by_id(bidId, username)


@router.put("/bids/{bidId}/status")
async def change_bid_status_by_id(
        bidId: int,
        status: BidStatus,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.change_bid_status_by_id(bidId, status, username)


@router.patch("/bids/{bidId}/edit")
async def edit_bid(
        bidId: int,
        bid_update_data: SBindUpdate,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.update_bid_by_id(bidId, bid_update_data, username)


@router.put("/bids/{bidId}/rollback/{version}")
async def rollback_bid(
        bidId: int,
        version: int,
        username: str,
        dao: BidDAO = Depends()
):
    return await dao.rollback_bid(bidId, version, username)
