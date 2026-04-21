from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import settings
from .api import user_router, service_router, booking_router
from .shared.exceptions import DomainException

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Booking API for managing users, services, and reservations",
)

app.include_router(user_router.router)
app.include_router(service_router.router)
app.include_router(booking_router.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.app_name}


@app.exception_handler(DomainException)
def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})
