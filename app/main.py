# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.otp.router import router as otp_router
from app.commands.router import router as admin_router
from app.ws.router import router as ws_router

app = FastAPI(title="EV Voice Assistant API")

# Preflight helper (каалга ачуу үчүн OPTIONS жооп)
@app.options("/{rest_of_path:path}")
def preflight_catch_all(rest_of_path: str, request: Request):
    return Response(status_code=204)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:65218",
        "http://localhost:50276",
        "https://ev-backendd.onrender.com",   # кааласаң калтырсаң болот
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)

# МАҢИЛҮҮСҮ: бул жерде prefix КОШПОО!
app.include_router(auth_router)    # auth_router'дын өзүндө prefix="/auth" бар
app.include_router(otp_router)     # otp_router'да prefix="/otp"
app.include_router(admin_router)   # commands -> prefix="/admin"
app.include_router(ws_router)      # ws -> prefix="/ws"
