from fastapi import APIRouter
from app.api.v1.endpoints import chat, feedback

api_router = APIRouter()

api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(feedback.router, tags=["feedback"])
