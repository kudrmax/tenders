from fastapi import APIRouter, Depends

from src.api.binds.dao import BindDAO
from src.api.binds.models import BindStatus
from src.api.binds.schemas import SBindCreate, SBindUpdate

router = APIRouter(
    prefix="/api",
    tags=["Binds"],
)


@router.post("/binds/new")
async def create_bind(
        tender: SBindCreate,
        dao: BindDAO = Depends()
):
    return await dao.create_bind(tender)


@router.get("/binds/my")
async def get_tenders_by_user(
        username: str,
        limit: int = 5,
        offset: int = 0,
        dao: BindDAO = Depends()
):
    return await dao.get_binds_by_kwargs(
        limit=limit,
        offset=offset,
        username=username
    )


@router.get("/binds/{tenderId}/list")
async def get_tenders_by_user(
        username: str,
        tenderId: int,
        limit: int = 5,
        offset: int = 0,
        dao: BindDAO = Depends()
):
    return await dao.get_binds_by_kwargs(
        limit=limit,
        offset=offset,
        username=username,
        tender_id=tenderId
    )


@router.get("/binds/{bindId}/status")
async def get_bind_status_by_id(
        bindId: int,
        username: str,
        dao: BindDAO = Depends()
):
    return await dao.get_bind_status_by_id(bindId, username)


@router.put("/binds/{bindId}/status")
async def change_bind_status_by_id(
        bindId: int,
        status: BindStatus,
        username: str,
        dao: BindDAO = Depends()
):
    return await dao.change_bind_status_by_id(bindId, status, username)


@router.patch("/binds/{bindId}/edit")
async def edit_bind(
        bindId: int,
        bind_update_data: SBindUpdate,
        username: str,
        dao: BindDAO = Depends()
):
    return await dao.update_bind_by_id(bindId, bind_update_data, username)


@router.put("/binds/{bindId}/rollback/{version}")
async def rollback_bind(
        bindId: int,
        version: int,
        username: str,
        dao: BindDAO = Depends()
):
    return await dao.rollback_bind(bindId, version, username)
