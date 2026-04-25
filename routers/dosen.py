from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import get_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def dosen_dashboard(request: Request):
    return templates.TemplateResponse("user/home.html", {"request": request})

@router.get("/riwayat", response_class=HTMLResponse)
def riwayat(request: Request):
    return templates.TemplateResponse("user/home.html", {"request": request})

@router.get("/penilaian", response_class=HTMLResponse)
def penilaian(request: Request):
    return templates.TemplateResponse("user/penilaian.html", {"request": request})