from fastapi import APIRouter
from api.endpoints import auth, users, places, friends, messages, search
# from app.api.endpoints import two_factor

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(two_factor.router, prefix="/2fa", tags=["2fa"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
api_router.include_router(friends.router, prefix="/friends", tags=["friends"])
api_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_router.include_router(search.router, prefix="/search", tags=["search"])