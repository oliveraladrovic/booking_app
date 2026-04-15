from fastapi import FastAPI

from .config import settings
from .api import user_router

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Booking API for managing users, services, and reservations",
)

app.include_router(user_router.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}
