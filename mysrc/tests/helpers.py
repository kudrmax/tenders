from sqlalchemy.ext.asyncio import AsyncSession
from mysrc.api.organisations.models import MOrganization
from mysrc.api.employees.models import MEmployee


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
