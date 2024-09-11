from typing import Any

from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mysrc.database import get_db


class DAO:
    def __init__(self, db=Depends(get_db)):
        self.db: AsyncSession = db

    async def _add_to_db(self, obj):
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj