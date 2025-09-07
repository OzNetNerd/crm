import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to import shared config
sys.path.append(str(Path(__file__).parent.parent))

from shared.database_config import DATABASE_URI, ASYNC_DATABASE_URI

# Async engine for FastAPI
async_engine = create_async_engine(
    ASYNC_DATABASE_URI,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URI else {}
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Sync engine for compatibility (if needed)
sync_engine = create_engine(
    DATABASE_URI,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URI else {}
)

SyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


# Dependency for FastAPI routes
async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_session():
    with SyncSessionLocal() as session:
        try:
            yield session
        finally:
            session.close()


# For testing
if __name__ == "__main__":
    print(f"Async Database URI: {ASYNC_DATABASE_URI}")
    print(f"Sync Database URI: {DATABASE_URI}")