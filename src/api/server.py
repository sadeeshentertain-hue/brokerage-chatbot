from fastapi import FastAPI
from src.api.v1.routes import v1_router
from src.config.settings import settings

app = FastAPI(title=settings.PROJECT_NAME)
app.include_router(v1_router, prefix="/api/v1")
