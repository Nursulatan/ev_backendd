# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Пакеттик (relative) импорттор — Render үчүн туура
from .auth.router import router as auth_router
from .otp.router import router as otp_router
from .commands.router import router as admin_router
from .ws.router import router as ws_router

app = FastAPI(title="EV Voice Assistant API")

# ---- Health check (/): Render сервери “тирүү” экенин ушу аркылуу текшерет ----
@app.get("/")
async def root():
    return {"status": "ok", "message": "EV backend is running 🚀"}

# ---- Кээ бир браузерлердин preflight OPTIONS суроолорун тынч кайтаруу (кааласаң калтыр) ----
@app.options("/{rest_of_path:path}")
def preflight_ok(rest_of_path: str, request: Request):
    return Response(status_code=204)

# ---- CORS: Flutter веб жана локалдык браузер үчүн уруксаттар ----
app.add_middleware(
    CORSMiddleware,
    # Так домендерди коштук; localhost'тун каалаган портуна regex да бар
    allow_origins=[
        "http://127.0.0.1",
        "http://localhost",
        "http://127.0.0.1:50076",
        "http://localhost:50076",
        # керек болсо өз фронтенд домениңди кош
        # "https://сенин-frontend-домениң",
    ],
    allow_origin_regex=r"^https?://localhost(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)

# ---- Роутерлер ----
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(otp_router, prefix="/otp", tags=["otp"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(ws_router, prefix="/ws", tags=["websocket"])
