# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.otp.router import router as otp_router
from app.commands.router import router as admin_router
from app.ws.router import router as ws_router

app = FastAPI()

@app.get("/")
@app.head("/")
def root():
    return{ "message": "EV backend is running 🚀"}
# Preflight helper (каалга ачуу үчүн OPTIONS жооп)
@app.options("/{rest_of_path:path}")
def preflight_catch_all(rest_of_path: str, request: Request):
    return Response(status_code=204)

# CORS

app.add_middleware(
    CORSMiddleware,
    # localhost/127.0.0.1 каалаган порттон уруксат
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d{1,5})?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# МАҢИЛҮҮСҮ: бул жерде prefix КОШПОО!
app.include_router(auth_router)    # auth_router'дын өзүндө prefix="/auth" бар
app.include_router(otp_router)     # otp_router'да prefix="/otp"
app.include_router(admin_router)   # commands -> prefix="/admin"
app.include_router(ws_router)      # ws -> prefix="/ws"
