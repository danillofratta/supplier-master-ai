import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


load_dotenv()


async def main() -> None:
    database_url = os.environ[
        "SAP_INTEGRATION_DATABASE_URL"
    ]

    print("Connecting to PostgreSQL...")

    engine = create_async_engine(
        database_url,
        echo=False,
    )

    async with engine.connect() as connection:
        result = await connection.execute(
            text("SELECT current_database()")
        )

        database_name = result.scalar_one()

        print(
            f"Connected successfully: {database_name}"
        )

        result = await connection.execute(
            text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        )

        print("Tables:")

        for row in result:
            print(f" - {row.table_name}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())