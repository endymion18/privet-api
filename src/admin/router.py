from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from src.auth.utils import get_current_user
from src.auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from src.database import get_async_session
from starlette import status

admin_router = APIRouter(
    tags=["Admin"]
)


@admin_router.post('/admin/role/change',
                   status_code=status.HTTP_200_OK)
async def change_user_role(email: str, role_id: int, current_user: User = Depends(get_current_user),
                           session: AsyncSession = Depends(get_async_session)):
    if current_user.role_id < 3:
        return JSONResponse({"error": "not allowed"}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    stmt = await session.execute(select(User).where(User.email == email))
    result = stmt.scalar()
    if result is None:
        return JSONResponse({"error": "email not found"})
    stmt = await session.execute(update(User)
                                 .where(User.email == email)
                                 .values(role_id=role_id))
    await session.commit()
    return JSONResponse({"details": "Роль изменена."})
