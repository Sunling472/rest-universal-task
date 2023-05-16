from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.common.config import get_config

CONFIG = get_config()

engine = create_async_engine(
    CONFIG.db.url,
    echo=CONFIG.db.db_echo_log
)

# noinspection PyTypeChecker
async_session: sessionmaker | AsyncSession = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
