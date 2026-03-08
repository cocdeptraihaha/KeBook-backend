"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    books,
    categories,
    cart,
    orders,
    reviews,
    promotions,
    return_requests,
    notifications,
    support_requests,
    test_utils,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["promotions"])
api_router.include_router(return_requests.router, prefix="/return-requests", tags=["return-requests"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(support_requests.router, prefix="/support-requests", tags=["support-requests"])
api_router.include_router(test_utils.router, prefix="/test", tags=["test"])
