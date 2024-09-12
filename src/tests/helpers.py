from sqlalchemy.ext.asyncio import AsyncSession
from src.api.organisations.models import MOrganization
from src.api.employees.models import MEmployee
from src.api.tenders.dao import TenderDAO
from src.api.tenders.schemas import STenderCreate


async def create_test_organization(
        async_session: AsyncSession,
        organization_name: str = "Test Organization",
) -> MOrganization:
    new_organization = MOrganization(name=organization_name, )
    async_session.add(new_organization)
    await async_session.commit()
    await async_session.refresh(new_organization)
    return new_organization


async def create_test_employee(
        async_session: AsyncSession,
        username: str = "test_username"
) -> MEmployee:
    new_employee = MEmployee(username=username)
    async_session.add(new_employee)
    await async_session.commit()
    await async_session.refresh(new_employee)
    return new_employee


async def create_test_tender(
        async_session: AsyncSession,
        s_new_tender: STenderCreate
):
    m_tender = await TenderDAO(db=async_session).create_tender(s_new_tender)
    return m_tender
