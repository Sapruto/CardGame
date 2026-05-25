from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

class Flash:
    def __init__(self, app: FastAPI, templates: Jinja2Templates):
        self.app = app
        self.templates = templates
        templates.env.globals["get_flash"] = self.get_flash
        self._register_routes()

    def _register_routes(self):
        @self.app.post("/send_flash")
        def send_flash(request: Request, msg: str = Form(...)):
            self.flash(request, msg, "success")
            return RedirectResponse(url="/", status_code=303)

    @staticmethod
    def flash(request: Request, message: str, category: str = "info"):
        if "_messages" not in request.session:
            request.session["_messages"] = []
        request.session["_messages"].append({"message": message, "category": category})

    @staticmethod
    def get_flash(request: Request):
        return request.session.pop("_messages") if "_messages" in request.session else []