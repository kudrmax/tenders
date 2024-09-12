from sqlalchemy import create_engine

from src.database.database import Base
from src.settings import settings

from src.api.tenders.models import MTender, MTenderData
from src.api.bids.models import MBind, MBindData
from src.api.organisations.models import MOrganization, MOrganizationResponsible
from src.api.employees.models import MEmployee


def init_db(
        create_organisations: bool = False,
        create_employee: bool = False,
):
    # tables = [
    #     MTender.__tablename__,
    #     MTenderData.__tablename__,
    #     MBind.__tablename__,
    #     MBindData.__tablename__
    # ]
    # if create_organisations:
    #     tables.append(MOrganization.__tablename__)
    #     tables.append(MOrganizationResponsible.__tablename__)
    # if create_employee:
    #     tables.append(MEmployee.__tablename__)

    sync_engine = create_engine(settings.db.url(is_async=False), echo=True)
    Base.metadata.create_all(
        bind=sync_engine,
        # tables=tables
    )


if __name__ == '__main__':
    init_db()
