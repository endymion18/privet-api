from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import auth_router, verify_router
from src.students.router import students_router
from src.university.router import university_router
from src.profile.router import profile_router
from src.arrivals.router import arrival_router, teamleader_router
from src.tasks.router import tasks_router
from src.messenger.router import messages_router
from src.admin.router import admin_router
from starlette.staticfiles import StaticFiles

app = FastAPI(
    title="Privet API"
)

origins = [
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(verify_router)
app.include_router(university_router)
app.include_router(profile_router)
app.include_router(arrival_router)
app.include_router(teamleader_router)
app.include_router(tasks_router)
app.include_router(messages_router)
app.include_router(admin_router)
app.include_router(students_router)

app.mount("/admin/", StaticFiles(directory="./src/admin/templates/", html=True))
app.include_router(students_router)
