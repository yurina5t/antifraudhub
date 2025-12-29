# app/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.home import home_route
from app.routes.user import user_route
#from app.routes.auth import auth_route
from app.routes.fraud import fraud_route
from app.database.database import init_db
from app.database.config import get_settings
from app.middleware.analytics import RequestLoggingMiddleware
from app.services.logging.logging import get_logger
import uvicorn

logger = get_logger(logger_name=__name__)
settings = get_settings()


def create_application() -> FastAPI:
    """
    Создание и конфигурация FastAPI приложения.
    """

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Routers
    app.include_router(home_route, tags=['Home'])
    #app.include_router(auth_route, prefix='/auth', tags=['Auth']) auth отключён для внутреннего сервиса
    app.include_router(user_route, prefix='/api/users', tags=['Users'])
    app.include_router(fraud_route, prefix="/api/fraud", tags=["Fraud"])

    return app


app = create_application()


@app.on_event("startup")
def on_startup():
    logger.info("Инициализация базы данных...")
    try:
        init_db()
        logger.info("Запуск приложения успешно завершён")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        raise


@app.on_event("shutdown")
def on_shutdown():
    logger.info("Остановка приложения...")


if __name__ == "__main__":
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
