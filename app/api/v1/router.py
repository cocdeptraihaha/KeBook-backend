"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin_dashboard,
    addresses,
    auth,
    users,
    books,
    book_discounts,
    book_details,
    categories,
    cart,
    orders,
    reviews,
    promotions,
    favorites,
    points,
    return_requests,
    notifications,
    support_requests,
    upload,
    test_utils,
)

api_router = APIRouter()

api_router.include_router(admin_dashboard.router, prefix="/admin")
api_router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(
    book_discounts.router, prefix="/book-discounts", tags=["book-discounts"]
)
api_router.include_router(book_details.router, prefix="/book-details", tags=["book-details"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(cart.router, prefix="/cart", tags=["cart"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(promotions.router, prefix="/promotions", tags=["promotions"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(points.router, prefix="/points", tags=["points"])
api_router.include_router(return_requests.router, prefix="/return-requests", tags=["return-requests"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(support_requests.router, prefix="/support-requests", tags=["support-requests"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(test_utils.router, prefix="/test", tags=["test"])
