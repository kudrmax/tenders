from pydantic_settings import BaseSettings


class DBSettingsBase:
    @property
    def url(self):
        return f'postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'

    @property
    def url_alembic(self):
        return f'postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}'


class DBSettings(BaseSettings, DBSettingsBase):
    host: str = '0.0.0.0'
    port: int = 5500
    username: str = 'postgres'
    password: str = 'postgres'
    database: str = 'crm'


class DBTestSettings(BaseSettings, DBSettingsBase):
    host: str = '0.0.0.0'
    port: int = 5501
    username: str = 'postgres_test'
    password: str = 'postgres_test'
    database: str = 'crm_test'


class Settings(BaseSettings):
    server_host: str = '0.0.0.0'
    server_port: int = 8000
    db: DBSettings = DBSettings()
    db_test: DBTestSettings = DBTestSettings()


settings = Settings(
    # _env_file='.env',
    # _env_file_encoding='utf-8',
)

# DB_URL = "postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres"
# DB_URL_FOR_ALEMBIC = "postgresql://postgres:postgres@0.0.0.0:5432/postgres"
# DB_URL_TEST = "postgresql+asyncpg://postgres_test:postgres_test@0.0.0.0:5433/postgres_test"
# DB_URL_FOR_ALEMBIC_TEST = "postgresql://postgres_test:postgres_test@0.0.0.0:5433/postgres_test"
