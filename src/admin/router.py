from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from src.auth.utils import get_current_user
from src.auth.models import User
from src.profile.models import Buddy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from src.database import get_async_session
from starlette import status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

admin_router = APIRouter(
    tags=["Admin"]
)


templates = Jinja2Templates(directory="./src/admin/templates")


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
    await session.execute(update(User)
                          .where(User.email == email)
                          .values(role_id=role_id))
    await session.commit()
    return JSONResponse({"details": "Роль изменена."})


@admin_router.post('/admin/buddy/confirm',
                   status_code=status.HTTP_200_OK)
async def confirm_buddy(email: str, current_user: User = Depends(get_current_user),
                        session: AsyncSession = Depends(get_async_session)):
    if current_user.role_id < 3:
        return JSONResponse({"error": "not allowed"}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    stmt = await session.execute(select(User.id).where(User.email == email))
    user_id = stmt.scalar()
    if user_id is None:
        return JSONResponse({"error": "email not found"})
    stmt = await session.execute(select(Buddy.user_id).where(Buddy.user_id == user_id))
    result = stmt.scalar()
    if result is None:
        return JSONResponse({"error": "buddy not found"})
    await session.execute(update(Buddy)
                          .where(Buddy.user_id == user_id)
                          .values(buddy_status=True))
    await session.commit()
    return JSONResponse({"details": "buddy confirmed"})


@admin_router.post('/admin/buddy/all')
async def get_all_buddies(current_user: User = Depends(get_current_user),
                          session: AsyncSession = Depends(get_async_session)):
    if current_user.role_id < 3:
        return JSONResponse({"error": "not allowed"}, status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
    stmt = await session.execute(select(User.email, Buddy.full_name, Buddy.buddy_status)
                                 .where(User.id == Buddy.user_id))
    result = stmt.fetchall()
    response = []
    for buddy in result:
        response.append({"email": buddy[0], "full_name": buddy[1], "confirmed": buddy[2]})
    return response


@admin_router.get("/admin/")
async def admin_page(request: Request):
    context = {'request': request}

    return templates.TemplateResponse(name="index.html", context=context)


@admin_router.get("/admin/login/")
async def admin_login_page(request: Request):
    context = {'request': request}
    return templates.TemplateResponse(name="login.html", context=context)
