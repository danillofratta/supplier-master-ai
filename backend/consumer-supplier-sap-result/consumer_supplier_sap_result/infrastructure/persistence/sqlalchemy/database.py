from consumer_supplier_sap_result.shared.observability import instrument_sqlalchemy

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
class Database:
    def __init__(self, database_url: str) -> None:
        self.engine=create_async_engine(database_url,pool_pre_ping=True)
        instrument_sqlalchemy(self.engine)
        self.session_factory=async_sessionmaker(self.engine,expire_on_commit=False)
