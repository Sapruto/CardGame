from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

base_router = APIRouter(tags=["users"])
templates = Jinja2Templates(directory="templates")

@base_router.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
