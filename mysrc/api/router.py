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
        tender_filter: STenderFilter = Depends(),
        dao: TenderDAO = Depends()
):
    return await dao.get_tenders_by_filter(tender_filter)


@router.get("/tenders/my")
async def get_tenders_by_filter(
        username: str,
        tender_filter: STenderLimitOffset = Depends(),
        dao: TenderDAO = Depends()
):
    return await dao.get_tenders_by_filter(tender_filter)


@router.post("/tender/new")
async def create_tender(
        tender: STenderCreate,
        dao: TenderDAO = Depends()
):
    return await dao.create(tender)
