"""
Script to initialize the database with tables
"""
from app.db.base import Base, engine
from app.db.models import Task, Report
from app.core.logger import log


def init_db():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        log.info("Database tables created successfully")
        print("SUCCESS: Database initialized successfully!")
        print(f"Tables created: {list(Base.metadata.tables.keys())}")
    except Exception as e:
        log.error(f"Error initializing database: {e}")
        print(f"ERROR: {e}")


if __name__ == "__main__":
    init_db()
