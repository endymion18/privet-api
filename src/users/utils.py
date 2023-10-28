from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User


async def email_exist(email: str, session: AsyncSession) -> bool:
    stmt = await session.execute(select(User.email).where(User.email == email))
    stmt = stmt.scalar()
    if stmt is None:
        return False
    else:
        return True
