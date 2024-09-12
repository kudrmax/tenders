import os

from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic_settings import BaseSettings

load_dotenv()


# DB_TEST_PATH = './test_test.db'
# DB_TEST_URL = f'sqlite+aiosqlite:///{DB_TEST_PATH}'
# DB_TEST_URL_SYNC = ''.join(DB_TEST_URL.split('+aiosqlite'))


class DBSettingsBase:
    # host = None
    # port = None
    # username = None
    # password = None
    # database = None

    @property
    def url(self):
        for data in [self.host, self.port, self.username, self.password, self.database]:
            if not data:
                raise HTTPException(status_code=500, detail='Database connection data has not been se tproperly')
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class DBSettings(BaseSettings, DBSettingsBase):
    host: str = os.getenv('POSTGRES_HOST')
    port: int = os.getenv('POSTGRES_PORT')
    username: str = os.getenv('POSTGRES_USERNAME')
    password: str = os.getenv('POSTGRES_PASSWORD')
    database: str = os.getenv('POSTGRES_DATABASE')


class Settings(BaseSettings):
    server_host: str = os.getenv('SERVER_ADDRESS').split(':')[0]
    server_port: int = int(os.getenv('SERVER_ADDRESS').split(':')[1])
    db: DBSettings = DBSettings()

settings = Settings()