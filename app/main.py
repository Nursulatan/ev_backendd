# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# .env жүктөө
load_dotenv()

# ❗ Салыштырма импорттор (алдына чекит бар)
from .auth import router as auth_router
from .otp import router as otp_router
from .commands import router as admin_router
from .ws import router as ws_router

app = FastAPI(title="EV Voice Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(admin_router)
app.include_router(ws_router)

@app.get("/")
def root():
    return {"ok": True}
