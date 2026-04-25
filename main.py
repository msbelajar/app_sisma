from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from routers import admin, dosen, test, auth
from security import verify_cookie_token

app = FastAPI(title="App Seminar")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Exception handler for 401 Unauthorized - redirect to login
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        return RedirectResponse(url="/login", status_code=303)
    raise exc

app.include_router(admin.router, prefix="/admin", dependencies=[Depends(verify_cookie_token)])
app.include_router(dosen.router, prefix="/dosen", dependencies=[Depends(verify_cookie_token)])
app.include_router(test.router, prefix="/test")
app.include_router(auth.router)