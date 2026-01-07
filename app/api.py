# app/api.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import init_db
from app.database.config import get_settings
from app.middleware.analytics import RequestLoggingMiddleware
from app.services.logging.logging import get_logger
from app.core.runtime import get_worker_mode

# Routers
from app.routes.home import home_route
from app.routes.user import user_route
from app.routes.fraud import fraud_route
from app.routes.gateway import gateway_route
from app.routes.ui import router as ui_router  


logger = get_logger(logger_name=__name__)
settings = get_settings()
WORKER_MODE = get_worker_mode()


def _register_routers(app: FastAPI) -> None:
    """
    Подключает роутеры в зависимости от WORKER_MODE.
    """
    logger.info(f"Starting service in WORKER_MODE={WORKER_MODE}")

    if WORKER_MODE == "api":
        # Public Gateway
        app.include_router(home_route, tags=["Home"])
        app.include_router(user_route, prefix="/api/users", tags=["Users"])
        app.include_router(gateway_route, prefix="/api", tags=["Gateway"])
        app.include_router(ui_router, prefix="/ui", include_in_schema=False)

    elif WORKER_MODE == "realtime":
        # Internal realtime worker
        app.include_router(fraud_route, prefix="/internal/fraud", tags=["Realtime"])

    elif WORKER_MODE == "batch":
        # Internal batch worker
        app.include_router(fraud_route, prefix="/internal/fraud", tags=["Batch"])

    else:
        raise RuntimeError(f"Unknown WORKER_MODE={WORKER_MODE}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing application...")

    if WORKER_MODE == "api":
        logger.info("Initializing database (gateway only)")
        try:
            init_db()
        except Exception as e:
            logger.error(f"Database init failed: {e}")
            raise
    else:
        logger.info("Skipping DB init (worker mode)")

    yield

    logger.info("Shutting down application")


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        lifespan=lifespan,
    )
    # STATIC FILES (CSS, JS)
    app.mount(
        "/static",
        StaticFiles(directory="app/view/static"),
        name="static",
    )

    # CORS (internal)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Routers by role
    _register_routers(app)

    return app


app = create_application()
