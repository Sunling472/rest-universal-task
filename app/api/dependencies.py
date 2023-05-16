from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordBearer

from app.db.session import async_session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/token/')


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
