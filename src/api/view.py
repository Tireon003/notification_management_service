import os
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

script_dir = os.path.dirname(__file__)
templates_dir = os.path.join(script_dir, "../templates")

templates = Jinja2Templates(directory=templates_dir)


@router.get("/", response_class=HTMLResponse)
async def get_notifications_page(
    request: Request,
) -> HTMLResponse:
    return templates.TemplateResponse(
        "notifications.html", {"request": request}
    )
