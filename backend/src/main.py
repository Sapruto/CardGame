from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager

from src.api.game_api import game_router
from src.api.admin_api import admin_router
from src.core.database import engine, Base, AsyncSessionLocal
from src.models.orm.metric_orm import MetricORM
from src.models.orm.character_orm import CharacterORM
from src.models.orm.question_orm import QuestionORM
from src.models.orm.answer_orm import AnswerORM
from src.models.orm.epilogue_orm import EpilogueORM
from src.models.orm.resource_orm import ResourceORM

import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

env_path = BASE_DIR / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("INIT_DB", "false").lower() == "true":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

def create_app() -> FastAPI:
    app_key = os.getenv("APP_SECRET_KEY")
    if not app_key:
        raise ValueError("APP_SECRET_KEY environment variable is required")

    app = FastAPI(title="Game API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(SessionMiddleware, secret_key=app_key)

    app.include_router(game_router)
    app.include_router(admin_router)

    FRONTEND_DIR = BASE_DIR / "frontend" / "build"
    MEDIA_DIR = BASE_DIR / "media"

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    for subdir in ["backgrounds", "characters", "cards"]:
        (MEDIA_DIR / subdir).mkdir(parents=True, exist_ok=True)

    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

    if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
        if (FRONTEND_DIR / "static").exists():
            app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

        @app.get("/{full_path:path}")
        async def serve_react(full_path: str):
            if full_path.startswith(("api/", "docs/", "redoc/", "openapi.json", "media/")):
                raise HTTPException(status_code=404)

            return FileResponse(FRONTEND_DIR / "index.html")

    return app

app = create_app()