from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.users.router import auth_router, verify_router
from src.university.router import university_router

app = FastAPI(
    title="Privet API"
)

origins = [
    "http://localhost"
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

