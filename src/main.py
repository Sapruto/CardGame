from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
from pathlib import Path

from src.api.game_api import game_router
from src.api.admin_api import admin_router
from src.base.TableManager import InitTables

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


def create_app() -> FastAPI:
    init = InitTables()
    init.initialize_tables()

    app_key = os.getenv("app_key")

    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=app_key)

    app.include_router(game_router)
    app.include_router(admin_router)

    FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "build"
    STATIC_DIR_B = Path(__file__).parent.parent / "static"
    STATIC_DIR_F = FRONTEND_DIR / "static"

    STATIC_DIR_B.mkdir(parents=True, exist_ok=True)
    (STATIC_DIR_B / "uploads" / "backgrounds").mkdir(parents=True, exist_ok=True)
    (STATIC_DIR_B / "uploads" / "characters").mkdir(parents=True, exist_ok=True)
    (STATIC_DIR_B / "uploads" / "cards").mkdir(parents=True, exist_ok=True)

    if STATIC_DIR_F.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR_F)), name="static_frontend")

    app.mount("/media", StaticFiles(directory=str(STATIC_DIR_B)), name="static_backend")

    @app.get("/{full_path:path}")
    async def serve_react(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            raise HTTPException(status_code=404)

        if full_path.startswith("static/") or full_path.startswith("media/"):
            raise HTTPException(status_code=404)

        index_path = FRONTEND_DIR / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="index.html not found")

    return app