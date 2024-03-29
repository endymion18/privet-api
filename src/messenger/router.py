import uuid
import datetime
import json
from src.database import get_async_session
from src.auth.utils import get_current_user
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, or_, and_
from starlette import status
from starlette.responses import JSONResponse
from src.auth.models import User
from src.messenger.models import Chat, Message
from src.messenger.wsmanager import manager
from src.messenger.schemas import GetChatSchema
from src.profile.models import Student, Buddy

messages_router = APIRouter(
    tags=["Messages"]
)


async def check_user(user_id: uuid.UUID, session: AsyncSession):
    stmt = await session.execute(select(User).where(User.id == user_id))
    result = stmt.scalar()
    return result is not None


@messages_router.post("/messages/chat/",
                      status_code=status.HTTP_200_OK)
async def create_chat(first_user: uuid.UUID, second_user: uuid.UUID,
                      session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute(select(Chat).where(or_(and_(Chat.first_user == first_user,
                                                             Chat.second_user == second_user),
                                                        and_(Chat.first_user == second_user,
                                                             Chat.second_user == first_user))))
    result = stmt.scalar()
    if result is not None:
        return JSONResponse({'details': 'err: chat with this params already exists'})
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

    if current_user.role_id == 1:
        support_chat = await session.execute(
            select(Chat).where(and_(Chat.first_user == uuid.UUID('6a0a716c-2728-4ad8-86a3-90a283653e4e'),
                                    Chat.second_user == user_id)))
        support_chat = support_chat.scalar()
        if support_chat is None:
            await create_chat(uuid.UUID('6a0a716c-2728-4ad8-86a3-90a283653e4e'), user_id, session)

    stmt = await session.execute(select(Chat).where(or_(Chat.first_user == user_id,
                                                        Chat.second_user == user_id)))
    chats = stmt.scalars().all()
    result = []
    for chat in chats:
        stmt = await session.execute(select(Student.full_name)
                                     .where(Student.user_id == chat.first_user))
        first_user_name = stmt.scalar()
        if first_user_name is None:
            stmt = await session.execute(select(Buddy.full_name)
                                         .where(Buddy.user_id == chat.first_user))
            first_user_name = stmt.scalar()
        stmt = await session.execute(select(Student.full_name)
                                     .where(Student.user_id == chat.second_user))
        second_user_name = stmt.scalar()
        if second_user_name is None:
            stmt = await session.execute(select(Buddy.full_name)
                                         .where(Buddy.user_id == chat.second_user))
            second_user_name = stmt.scalar()
        stmt = await session.execute(select(Message)
                                     .where(Message.chat_id == chat.id)
                                     .order_by(Message.date_print.desc()))
        last_message = stmt.scalar()

        if chat.first_user == uuid.UUID('6a0a716c-2728-4ad8-86a3-90a283653e4e'):
            first_user_name = 'Поддержка'

        result.append(GetChatSchema(user_id, chat, first_user_name, second_user_name, last_message))
    return result


@messages_router.get("/messages/{chat_id}")
async def get_chat_messages(chat_id: int, count: int = 100, offset: int = 0,
                            session: AsyncSession = Depends(get_async_session)):
    stmt = await session.execute(select(Message)
                                 .where(Message.chat_id == chat_id)
                                 .order_by(Message.date_print.asc())  # в возрастающем или убывающем порядке???
                                 .offset(offset)
                                 .limit(count))
    result = stmt.scalars().all()
    return result


@messages_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket,
                             session: AsyncSession = Depends(get_async_session), token: str = Query(...)):
    current_user = await manager.add_connection(websocket, token)
    if current_user is None:
        return
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
            data = json.loads(data)
            if "type" not in data:
                continue
            if data["type"] == "send_message":
                current_datetime = datetime.datetime.now()
                await session.execute(insert(Message)
                                      .values(chat_id=data["chat_id"], from_user=current_user.id,
                                              date_print=current_datetime,
                                              attachment='', text=data["text"], read=False))
                await session.commit()
                await manager.send_message(data["type"], current_user.id, data["chat_id"],
                                           data["text"])
    except WebSocketDisconnect:
        manager.remove_connection(websocket)
