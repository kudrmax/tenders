from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mysrc.database import get_db


class DAO:
    def __init__(self, db=Depends(get_db)):
        self.db: AsyncSession = db


class CRUD(DAO):
    crud_model = None

    async def create_object(self, object: crud_model):
        self.db.add(object)
        await self.db.commit()
        return object
