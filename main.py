from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from routers import admin, dosen, test, auth, root
from security import verify_cookie_token

app = FastAPI(title="App Seminar")

# Better than custom HTTPS middleware
app.add_middleware(ProxyHeadersMiddleware)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Temporary debug endpoint to check headers
@app.get("/debug-headers")
async def debug_headers(request: Request):
    return {
        "scheme": request.url.scheme,
        "x-forwarded-proto": request.headers.get('x-forwarded-proto'),
        "x-forwarded-for": request.headers.get('x-forwarded-for'),
        "host": request.headers.get('host'),
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 401:
        return RedirectResponse(url="/login", status_code=303)
    raise exc

app.include_router(root.router)
app.include_router(admin.router, prefix="/admin", dependencies=[Depends(verify_cookie_token)])
app.include_router(dosen.router, prefix="/dosen", dependencies=[Depends(verify_cookie_token)])
app.include_router(test.router, prefix="/test")
app.include_router(auth.router)