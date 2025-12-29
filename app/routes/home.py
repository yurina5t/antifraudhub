# app/routes/home.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_optional_user
from typing import Dict

home_route = APIRouter()
templates = Jinja2Templates(directory="app/view")


@home_route.get("/", response_class=HTMLResponse)
async def index(request: Request, user=Depends(get_optional_user)):
    """
    Главная страница антифрод-сервиса.
    Если пользователь залогинен — передаём user в шаблон.
    Если нет — user=None.
    """
    context = {
        "request": request,
        "user": user,
    }
    return templates.TemplateResponse("index.html", context)


@home_route.get("/health", response_model=Dict[str, str])
async def health_check():
    return {"status": "healthy"}

