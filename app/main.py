# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.ai.router import router as ai_router
from app.assistant.router import router as assistant_router
from app.car.router import router as car_router
from app.gateway.router import router as gateway_ws_router
# from app.gateway.token_router import router as gateway_token_router # type: ignore
from app.otp.router import router as otp_router
from app.auth.router import router as auth_router
app = FastAPI(title="Car Assistant (Local + Gemini)")

@app.get("/")
@app.head("/")
def root():
    return {"message": "EV backend is running 🚀"}

# OPTIONS preflight
@app.options("/{rest_of_path:path}")
def preflight_catch_all(rest_of_path: str, request: Request):
    return Response(status_code=204)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d{1,5})?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)
app.include_router(assistant_router)
# ... башка include'дар ...
app.include_router(car_router)  # /car/...
app.include_router(auth_router)
# app.include_router(gateway_token_router)
app.include_router(gateway_ws_router)
app.include_router(otp_router)
# app.include_router(tts)