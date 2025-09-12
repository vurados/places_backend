from .auth import router as auth_router
from .users import router as users_router
from .places import router as places_router
from .friends import router as friends_router
from .messages import router as messages_router
from .search import router as search_router
from .notifications import router as notifications_router

__all__ = [
    "auth_router",
    "users_router",
    "places_router",
    "friends_router",
    "messages_router",
    "search_router",
    "notifications_router"
]