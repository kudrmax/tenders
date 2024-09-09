from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from mysrc.database import get_db


class DAO:
    model = None

    def __init__(self, db=Depends(get_db)):
        self.db: AsyncSession = db

    async def get_all(self) -> List[model]:
        query = select(self.model)
        return list((await self.db.execute(query)).scalars().all())

    async def get_one_or_none_by_id(self, id) -> Optional[model]:
        query = select(self.model).where(self.model.id == id)
        return (await self.db.execute(query)).scalar_one_or_none()

    async def get_all_with_filter(self, *args, **kwargs) -> List[model]:
        query = select(self.model).filter_by(**kwargs)
        return list((await self.db.execute(query)).scalars().all())

    async def get_one_or_none_with_filter(self, *args, **kwargs) -> Optional[model]:
        query = select(self.model).filter_by(**kwargs)
        return (await self.db.execute(query)).scalar_one_or_none()

    async def get_one_by_id(self, id):
        obj = await self.get_one_or_none_by_id(id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"Object with {id = } not found in databse {self.model}.")
        return obj
