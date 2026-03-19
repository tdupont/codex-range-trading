from fastapi import FastAPI

from app.api.routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Range Trading Screener API",
        version="0.1.0",
        description="FastAPI backend for the Range Trading Screener MVP.",
    )
    app.include_router(api_router)
    return app


app = create_app()
