from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mysrc.database import get_db


class DAO:
    def __init__(self, db=Depends(get_db)):
        self.db: AsyncSession = db
