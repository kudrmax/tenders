import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.api.tenders.router import router as tenders_router
from src.api.binds.router import router as binds_router
from src.database import init_db
from src.api.tenders.models import MTender, MTenderData
from src.api.binds.models import MBind, MBindData
from src.api.organisations.models import MOrganization, MOrganizationResponsible
from src.api.employees.models import MEmployee

app = FastAPI(title='Avito')
app.include_router(tenders_router)
app.include_router(binds_router)


@app.get("/")
def root():
    return RedirectResponse('/docs')


if __name__ == '__main__':
    init_db()
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)
