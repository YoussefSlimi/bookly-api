import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.auth.routers import auth_router
from src.books.routes import book_router
from src.db.main import init_db
from src.reviews.routes import review_router
from src.tags.routes import tags_router

from .errors import register_all_errors
from .middleware import register_middleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bookly.app")


@asynccontextmanager
async def life_span(app: FastAPI):
    logger.info("server is starting ...")
    if os.getenv("ENV", "development") != "production":
        await init_db()
    yield
    logger.info("server has been stopped")


version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service",
    version=version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=life_span,
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/license/mit/",
    },
    contact={
        "name": "Slimy Youssef",
        "email": "slimyyoussef@gmail.com",
    },
)

register_all_errors(app)
register_middleware(app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["review"])
app.include_router(tags_router, prefix=f"/api/{version}/tags", tags=["tags"])

