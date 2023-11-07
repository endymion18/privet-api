from sqlalchemy import update, select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import WrongToken, WrongEmail
from src.auth.models import User, Token
from src.auth.utils import generate_confirmation_token, send_email


async def send_token(email: str, session: AsyncSession):

    email_from_db = await session.execute(select(User.email).where(User.email == email))
    if email_from_db.scalar() is None:
        raise WrongEmail("This user does not exist")

    stmt = await session.execute(select(Token).where(Token.email == email))
    token = await generate_confirmation_token()
    if stmt.scalar() is not None:
        await session.execute(update(Token).where(Token.email == email).values(token=token))
    else:
        await session.execute(insert(Token).values(email=email, token=token))
    await session.commit()

    await send_email(email, token)


async def check_token(email: str, token: str, session: AsyncSession):
    stmt = await session.execute(select(Token.token).where(Token.email == email))
    required_token = stmt.scalar()
    if required_token == token:
        await session.execute(delete(Token).where(Token.email == email))
        await session.execute(update(User).where(User.email == email).values(email_verified=True))
        await session.commit()
    else:
        raise WrongToken("Token is incorrect")
