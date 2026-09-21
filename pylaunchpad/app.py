"""FastAPI application factory, middleware, and route mounting."""

import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pylaunchpad.config import settings
from pylaunchpad.database import init_db
from pylaunchpad.tasks.worker import task_worker
from pylaunchpad.api import api_v1_router

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context managing database schema and background task workers."""
    # Startup
    init_db()
    await task_worker.start()
    yield
    # Shutdown
    await task_worker.stop()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade FastAPI micro-SaaS and AI API starter kit with Polar.sh billing.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Security Headers & Performance Middleware
    @app.middleware("http")
    async def add_security_headers_and_timing(request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        response: Response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

    # 3. Mount Static Files
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # 4. Mount API Routes
    app.include_router(api_v1_router)

    # 5. Template Engine
    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    # 6. Web Page Routes
    @app.get("/", tags=["Web Pages"])
    async def index_page(request: Request):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "polar_env": settings.POLAR_ENVIRONMENT,
            },
        )

    @app.get("/login", tags=["Web Pages"])
    async def login_page(request: Request):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "app_name": settings.APP_NAME},
        )

    @app.get("/register", tags=["Web Pages"])
    async def register_page(request: Request):
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "app_name": settings.APP_NAME},
        )

    @app.get("/dashboard", tags=["Web Pages"])
    async def dashboard_page(request: Request):
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "app_name": settings.APP_NAME},
        )

    return app


app = create_app()
