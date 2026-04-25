from fastapi import APIRouter, HTTPException, status, Depends, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/notfound", response_class=HTMLResponse)
def not_found(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})