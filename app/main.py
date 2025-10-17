# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.otp.router import router as otp_router
from app.commands.router import router as admin_router
from app.ws.router import router as ws_router
from app.ai.router import router as ai_router

app = FastAPI(title="AI Backend (Gemini version)")

@app.get("/")
@app.head("/")
def root():
    return {"message": "EV backend is running 🚀"}

@app.options("/{rest_of_path:path}")
def preflight_catch_all(rest_of_path: str, request: Request):
    return Response(status_code=204)

# Эгер фронт Render/башка доменде болсо – убактылуу баарына уруксат:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # кааласаң домендерди такта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)
app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(admin_router)
app.include_router(ws_router)
