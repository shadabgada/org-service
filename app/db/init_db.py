import logging
from sqlalchemy import create_engine
from app.core.config import settings
from app.models.base import Base
from app.models.employee import Employee
from app.models.org_chart import OrgChart

logger = logging.getLogger(__name__)


async def init_db():
    try:
        engine = create_engine(settings.DATABASE_URL)

        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise