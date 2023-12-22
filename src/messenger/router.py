import uuid
import datetime
from src.database import get_async_session
from src.auth.utils import get_current_user
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from starlette import status
from starlette.responses import JSONResponse
from src.auth.models import User
from src.messenger.models import Chat, Message

messages_router = APIRouter(
    tags=["messages"]
)


async def check_user(user_id: uuid.UUID, session: AsyncSession):
    stmt = await session.execute(select(User).where(User.id == user_id))
    result = stmt.scalar()
    return result is not None


@messages_router.post("/messages/chat/",
                      status_code=status.HTTP_200_OK)
async def create_chat(first_user: uuid.UUID, second_user: uuid.UUID,
                      session: AsyncSession = Depends(get_async_session)):
    if await check_user(first_user, session) and await check_user(second_user, session):
        await session.execute(insert(Chat).values(first_user=first_user,
                                                  second_user=second_user))
        await session.commit()
        return JSONResponse({"details": "chat created"})
    return JSONResponse({"details": "no user found"}, status_code=400)


@messages_router.get("/messages/chat/",
                      status_code=status.HTTP_200_OK)
async def get_user_chats(current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_async_session)):
    user_id = current_user.id
    stmt = await session.execute(select(Chat).where(Chat.first_user == user_id
                                                    or Chat.second_user == user_id))
    result = stmt.scalar()
    return result


@messages_router.post("/messages/send/")
async def create_message(chat_id: int, text: str, attachment: str = "",
                         current_user: User = Depends(get_current_user),
                         session: AsyncSession = Depends(get_async_session)):
    user_id = current_user.id
    current_datetime = datetime.datetime.now()
    await session.execute(insert(Message)
                          .values(chat_id=chat_id, from_user=user_id,
                                  date_print=current_datetime,
                                  attachment=attachment, text=text))

