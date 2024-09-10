from fastapi import APIRouter

router = APIRouter(
    prefix="/api",
    tags=["Binds"],
)

@router.get("/binds/")
async def binds():
    pass

# @router.post("/tender/new")
# async def create_tender(
#         tender: STenderCreate,
#         dao: TenderDAO = Depends()
# ):
#     return await dao.create_tender(tender)
#
#
# @router.get("/tenders/")
# async def get_all_tenders_by_filter(
#         limit: int = 5,
#         offset: int = 0,
#         service_type: Optional[TenderServiceType] = None,
#         dao: TenderDAO = Depends()
# ):
#     return await dao.get_tenders_by_kwargs(
#         limit=limit,
#         offset=offset,
#         service_type=service_type
#     )
#
#
# @router.get("/tenders/my")
# async def get_tenders_by_user(
#         username: str,
#         limit: int = 5,
#         offset: int = 0,
#         dao: TenderDAO = Depends()
# ):
#     return await dao.get_tenders_by_kwargs(
#         limit=limit,
#         offset=offset,
#         username=username
#     )
#
#
# @router.get("/tenders/{tenderId}/status")
# async def get_tender_status_by_id(
#         tenderId: int,
#         username: str,
#         dao: TenderDAO = Depends()
# ):
#     return await dao.get_tender_status_by_id(tenderId, username)
#
#
# @router.put("/tenders/{tenderId}/status")
# async def change_tender_status_by_id(
#         tenderId: int,
#         status: TenderStatus,
#         username: str,
#         dao: TenderDAO = Depends()
# ):
#     return await dao.change_tender_status_by_id(tenderId, status, username)
#
#
# @router.patch("/tenders/{tenderId}/edit")
# async def change_tender_status_by_id(
#         tenderId: int,
#         tender_update_data: STenderUpdate,
#         username: str,
#         dao: TenderDAO = Depends()
# ):
#     return await dao.update_tender_by_id(tenderId, tender_update_data, username)
#
#
# @router.put("/tenders/{tenderId}/rollback/{version}")
# async def change_tender_status_by_id(
#         tenderId: int,
#         version: int,
#         username: str,
#         dao: TenderDAO = Depends()
# ):
#     return await dao.rollback_tender(tenderId, version, username)
#
