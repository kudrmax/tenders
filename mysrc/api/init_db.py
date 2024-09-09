import uuid

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from mysrc.database import get_db
from mysrc.api.models import MEmployee, MOrganization, MOrganizationResponsible


async def create_objects(db: AsyncSession):
    new_employee = MEmployee(
        username="kudrmax",
        first_name="Max",
        last_name="Kudryashov"
    )
    db.add(new_employee)
    try:
        await db.commit()
        await db.refresh(new_employee)
    except Exception:
        await db.rollback()
        pass

    new_organization = MOrganization(
        name="HSE",
        description="Higher School of Economics",
    )
    db.add(new_organization)
    try:
        await db.commit()
        await db.refresh(new_organization)
    except Exception as e:
        await db.rollback()
        print(e)

    # new_responsible = MOrganizationResponsible(
    #     organization_id=new_organization.id,
    #     user_id=new_employee.id
    # )
    # db.add(new_responsible)
    # await db.commit()
    # await db.refresh(new_responsible)

    return {
        "employee": new_employee,
        "organization": new_organization,
        # "responsible": new_responsible
    }


router = APIRouter()


@router.post("/create-test-data/")
async def create_sample_data(db: AsyncSession = Depends(get_db)):
    created_objects = await create_objects(db)
    return created_objects
