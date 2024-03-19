from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(
    tags=['views']
)


templates = Jinja2Templates(directory='../../templates')


@router.get("/register")
async def get_register_template(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/register_gratitude")
async def get_register_gratitude_template(request: Request, email: str):
    return templates.TemplateResponse("after_register.html", {"request": request, "email": email})


@router.get("/register_confirm")
async def get_register_confirm_template(request: Request):
    return templates.TemplateResponse("confirm_register.html", {"request": request})


@router.get("/login")
async def get_login_template(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/profile")
async def get_profile_template(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/profile/edit")
async def get_edit_profile_template(request: Request):
    return templates.TemplateResponse("edit_profile.html", {"request": request})


@router.get("/card")
async def get_card_template(request: Request):
    return templates.TemplateResponse("card.html", {"request": request})


@router.get("/pass")
async def get_pass_template(request: Request, token: str):
    return templates.TemplateResponse("pass.html", {"request": request, "token": token})
