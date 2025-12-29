# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from app.auth.hash_password import HashPassword
from app.auth.jwt_handler import create_access_token
from app.database.database import get_session
from app.services.auth.loginform import LoginForm
from app.services.crud import user as UsersService
from app.database.config import get_settings

INTERNAL_MODE = True
# Получаем настройки приложения
settings = get_settings()
auth_route = APIRouter()
hash_password = HashPassword()
templates = Jinja2Templates(directory="app/view")

@auth_route.post("/token")
async def login_for_access_token(
    response: Response, 
    form_data: OAuth2PasswordRequestForm=Depends(), 
    session=Depends(get_session)
) -> dict[str, str]:
    """
    Создает access token для аутентифицированного пользователя.
    """    
    # Проверяем существование пользователя по email
    #user_exist = UsersService.get_user_by_email(form_data.username, session)
    #if user_exist is None:
    #    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist")
    
    # Проверяем правильность пароля
    #if hash_password.verify_hash(form_data.password, user_exist.password):
        # Создаем JWT токен
    #    access_token = create_access_token({
    #        "user_id": user_exist.id,
    #        "email": user_exist.email,
    #        "is_admin": user_exist.is_admin
    #    })

    #    response.set_cookie(
    #        key=settings.COOKIE_NAME, 
    #        value=f"Bearer {access_token}", 
    #        httponly=True
    #    )
        
        # Возвращаем токен в ответе
    #    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}

    #raise HTTPException(
    #    status_code=status.HTTP_401_UNAUTHORIZED,
    #    detail="Invalid details passed."
    #)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication is disabled (internal service)",
    )

@auth_route.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    """
    Отображает страницу входа.

    Args:
        request (Request): Объект HTTP-запроса

    Returns:
        TemplateResponse: HTML-страница с формой входа
    """
    # Передаем объект запроса в шаблон
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)
    
@auth_route.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, session=Depends(get_session)):

    """
    Обрабатывает отправку формы входа.

    Args:
        request (Request): Объект HTTP-запроса
        session (Session): Сессия базы данных

    Returns:
        Response: Перенаправление на главную страницу при успехе
        или HTML-страница с ошибками при неудаче
    """
    if INTERNAL_MODE:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    # Создаем и валидируем форму входа
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            # При успешной валидации перенаправляем на главную
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form, session=session)
            form.__dict__.update(msg="Login Successful!")
            print("[green]Login successful!!!!")
            return response
        except HTTPException:
            # При ошибке аутентификации показываем сообщение об ошибке
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)

@auth_route.get("/logout", response_class=HTMLResponse)
async def logout():
    """
    Выполняет выход пользователя из системы.

    Returns:
        RedirectResponse: Перенаправление на главную страницу
        с удалением cookie авторизации
    """
    # Создаем редирект и удаляем cookie с токеном
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response
