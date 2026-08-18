from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

class Database:
    """Connection factory for the SAP Integration service-owned PostgreSQL database."""
    def __init__(self, database_url: str) -> None:
        self.engine = create_async_engine(database_url, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
