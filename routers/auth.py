import os

from fastapi import APIRouter, HTTPException, status, Depends, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import get_db, Dosen
from security import checkpass, create_access_token
from schemas import Role
from typing import Optional

router = APIRouter()
expires_week: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_WEEKS"))
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login(request: Request, access_token: Optional[str] = Cookie(None)):
    # If user already has a valid token, redirect to their dashboard
    if access_token:
        return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    dosen = db.query(Dosen).filter(Dosen.nip == username).first()
    if dosen:
        if checkpass(password, dosen.password):
            # Create access token
            token_data = {"sub": dosen.nip, "role": dosen.role}
            access_token = create_access_token(token_data)
            
            # Create response and set cookie
            if dosen.role == Role.admin:
                response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
            else:
                response = RedirectResponse(url="/dosen", status_code=status.HTTP_303_SEE_OTHER)
            
            # Set cookie with token
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax",
                max_age=60*60*24*7*expires_week  # in weeks
            )
            return response
        else:
            msg = "Password salah"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    msg = "Data dosen tidak ada"
    return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response

