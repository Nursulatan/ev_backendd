from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# 🔧 Пакеттик (relative) импорттор – бул абдан маанилүү!

from app.auth import router as auth_router
from app.otp import router as otp_router
from app.commands import router as admin_router
from app.ws import router as ws_router


# -------------------------------------------------------
#  🧠 FastAPI тиркемесин түзөбүз
# -------------------------------------------------------
app = FastAPI(title="EV Voice Assistant API")


@app.get("/")
async def root():
    return {"status": "ok", "message": "EV backend is running 🚀"}
# -------------------------------------------------------
#  🛠️ Preflight (OPTIONS) жооп – CORS текшерүүсү үчүн
# -------------------------------------------------------
@app.options("/{rest_of_path:path}")
def preflight_catch_all(rest_of_path: str, request: Request):
    return Response(status_code=204)


# -------------------------------------------------------
#  🌍 CORS Орнотуулары
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:65218",
        "http://localhost:50276",
        "https://senin-frontend-domenin.kg",  # өз фронтенд домениңди бул жакка жаз
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Authorization"],
)


# -------------------------------------------------------
#  📦 Роутерлерди кошобуз
# -------------------------------------------------------
app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(admin_router)
app.include_router(ws_router)
