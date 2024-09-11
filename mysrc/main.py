import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from mysrc.api.tenders.router import router as tenders_router
from mysrc.api.binds.router import router as binds_router
from mysrc.database import init_db
from mysrc.api.tenders.models import MTender, MTenderData
from mysrc.api.binds.models import MBind, MBindData
from mysrc.api.organisations.models import MOrganization, MOrganizationResponsible
from mysrc.api.employees.models import MEmployee

app = FastAPI(title='Avito')
app.include_router(tenders_router)
app.include_router(binds_router)


@app.get("/")
def root():
    return RedirectResponse('/docs')


if __name__ == '__main__':
    init_db()
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)