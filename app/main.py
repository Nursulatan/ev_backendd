# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .otp import router as otp_router
from .commands import router as admin_router
from .ws import router as ws_router
from fastapi import Request, Response

@app.options("/{rest_of_path:path}")
def preflight_catch_all(rest_of_path: str, request: Request):
    return Response(status_code=204)

app = FastAPI(title="EV Voice Assistant API")

# ---- CORS: Flutter веб (жергиликтүү) үчүн уруксаттар ----


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:65218",   # сенин Flutter web портуң
        "http://localhost:50076",
        "https://senin-frontend-domenin.kg",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)


# ---- Роуттар ----
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(otp_router, prefix="/otp", tags=["otp"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(ws_router, prefix="/ws", tags=["ws"])

# ---- Healthcheck / Root (Koyeb/Render текшерүүсү үчүн пайдалуу) ----
@app.get("/", tags=["meta"])
def root():
    return {"ok": True, "service": "ev-backend"}

@app.get("/health", tags=["meta"])
def health():
    return {"status": "healthy"}
