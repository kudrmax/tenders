# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette.testclient import TestClient
#
# from src.api.tenders.models import TenderServiceType, TenderStatus
# from src.api.tenders.schemas import STenderCreate
# from src.tests.helpers import create_test_organization, create_test_employee, create_test_tender
#
#
# async def test_get_all_tenders(client: TestClient, async_session: AsyncSession):
#     # response = client.get("/api/tenders/")
#     # assert response.status_code == 200
#     # response_data = response.json()
#     # assert isinstance(response_data, list)
#     # assert len(response_data) == 0
#
#     new_organization = await create_test_organization(async_session)
#     new_employee = await create_test_employee(async_session)
#     await create_test_tender(async_session, STenderCreate(
#         name='Tender name',
#         description='Tender description',
#         serviceType=TenderServiceType.construction,
#         status=TenderStatus.created,
#         organizationId=new_organization.id,
#         creatorUsername=new_employee.username
#     ))
#     await create_test_tender(async_session, STenderCreate(
#         name='Tender nam 2',
#         description='Tender description',
#         serviceType=TenderServiceType.construction,
#         status=TenderStatus.created,
#         organizationId=new_organization.id,
#         creatorUsername=new_employee.username
#     ))
#
#     response = client.get("/api/tenders/")
#     assert response.status_code == 200
#
#     response_data = response.json()
#     assert isinstance(response_data, list)
#     assert len(response_data) == 2
#
#     tender = response_data[0]
#     assert "name" in tender
#     assert "description" in tender
#     assert "status" in tender
#     assert "serviceType" in tender
#     assert "version" in tender
#
# # async def test_get_all_tenders_by_service_type(client: TestClient, async_session: AsyncSession):
# #     new_organization = await create_test_organization(async_session)
# #     new_employee = await create_test_employee(async_session)
# #
# #     await create_test_tender(async_session, new_organization.id, new_employee.username, TenderServiceType.construction)
# #
# #     response = client.get("/api/tenders/", params={"service_type": TenderServiceType.construction})
# #     assert response.status_code == 200
# #
# #     response_data = response.json()
# #     assert isinstance(response_data, list)
# #     assert len(response_data) > 0
# #
# #     for tender in response_data:
# #         assert tender["serviceType"] == TenderServiceType.construction
