from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from mysrc.api.dao import TenderDAO
from mysrc.api.models import TenderServiceType
from mysrc.api.schemas import STenderCreate, STenderFilter, STenderLimitOffset

router = APIRouter(
    prefix="/api",
    tags=["Router"],
)


@router.get("/tenders/")
async def get_tenders_by_filter(
        limit: int = 5,
        offset: int = 0,
        service_type: Optional[TenderServiceType] = None,
        dao: TenderDAO = Depends()
):
    return await dao.get_tenders_by_kwargs(
        limit=limit,
        offset=offset,
        service_type=service_type
    )


@router.get("/tenders/my")
async def get_tenders_by_filter(
        username: str,
        limit: int = 5,
        offset: int = 0,
        dao: TenderDAO = Depends()
):
    return await dao.get_tenders_by_kwargs(
        limit=limit,
        offset=offset,
        username=username
    )


@router.post("/tender/new")
async def create_tender(
        tender: STenderCreate,
        dao: TenderDAO = Depends()
):
    return await dao.create(tender)
