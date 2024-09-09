import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from mysrc.api.router import router
from mysrc.api.init_db import router as router_init_db
import mysrc.api.models
from mysrc.database import init_db

app = FastAPI(title='Avito')
app.include_router(router)
app.include_router(router_init_db)


@app.get("/")
def root():
    return RedirectResponse('/docs')


if __name__ == '__main__':
    init_db()
    uvicorn.run('main:app', host='0.0.0.0', port=8080, reload=True)
