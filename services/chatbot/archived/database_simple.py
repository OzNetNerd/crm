import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path to import shared config
sys.path.append(str(Path(__file__).parent.parent))

from shared.database_config import DATABASE_URI

# Create sync engine for now (will upgrade to async later)
sync_engine = create_engine(
    DATABASE_URI,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URI else {},
)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


# Dependency for FastAPI routes
def get_sync_session():
    with SyncSessionLocal() as session:
        try:
            yield session
        finally:
            session.close()


# For testing
if __name__ == "__main__":
    print(f"Database URI: {DATABASE_URI}")

    # Test connection
    try:
        with SyncSessionLocal() as session:
            result = session.execute(text("SELECT 1"))
            print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
