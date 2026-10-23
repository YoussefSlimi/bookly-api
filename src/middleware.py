import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.requests import Request

from src.config import Config

logger = logging.getLogger("bookly.middleware")


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        processing_time = time.time() - start_time
        message = (
            f"{request.method} - {request.url.path} - {response.status_code} "
            f"completed after {processing_time:.3f}s"
        )
        logger.info(message)
        return response

    allowed_origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    if Config.DOMAIN:
        if Config.DOMAIN.startswith(("http://", "https://")):
            allowed_origins.append(Config.DOMAIN)
        else:
            allowed_origins.extend([f"http://{Config.DOMAIN}", f"https://{Config.DOMAIN}"])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(dict.fromkeys(allowed_origins)),
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    domain_host = Config.DOMAIN
    if domain_host.startswith("http://"):
        domain_host = domain_host[7:]
    elif domain_host.startswith("https://"):
        domain_host = domain_host[8:]

    hostname = domain_host.split(":")[0] if domain_host else "localhost"
    allowed_hosts = list(dict.fromkeys(["localhost", "127.0.0.1", hostname]))

    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
