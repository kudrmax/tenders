import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.tenders.router import router as tenders_router
from src.api.bids.router import router as binds_router

from src.database.database import get_db
from src.database.init_database import init_db

from src.api.employees.models import MEmployee
from src.api.organisations.models import MOrganization, MOrganizationResponsible
from src.settings import settings

app = FastAPI(title='Avito Tender Management API')
app.include_router(tenders_router)
app.include_router(binds_router)


@app.get("/")
def root():
    return RedirectResponse('/docs')


@app.get("/ping")
def ping():
    return "ok"


@app.get("/employee/get_all")
async def get_all_employee(db: AsyncSession = Depends(get_db)):
    quety = select(MEmployee)
    res = await db.execute(quety)
    return res.scalars().all()


@app.get("/organisation/get_all")
async def get_all_organisaion(db: AsyncSession = Depends(get_db)):
    quety = select(MOrganization)
    res = await db.execute(quety)
    return res.scalars().all()


@app.get("/organisation_responsible/get_all")
async def get_all_organisation_responsible(db: AsyncSession = Depends(get_db)):
    quety = select(MOrganizationResponsible)
    res = await db.execute(quety)
    return res.scalars().all()


if __name__ == '__main__':
    # init_db()
    uvicorn.run(
        'main:app',
        host=settings.server_host,
        port=settings.server_port,
        reload=True
    )
