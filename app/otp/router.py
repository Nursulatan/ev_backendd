from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS кошуу
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Productionдо белгилүү домендерди коюңуз
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/otp", tags=["OTP"])

# Кодду сактоо үчүн сөздүк. Чыныгы проектте база данных колдонуңуз.
otp_storage = {}

class OtpCode(BaseModel):
    code: str

@router.post("/generate")
async def generate_otp():
    # 6-цифралуу рандом код генерациялоо
    code = ''.join(secrets.choice('0123456789') for _ in range(6))
    # Убакытты белгилоо (азыркы убакыт + 10 мүнөт)
    expires_at = datetime.now() + timedelta(minutes=10)
    otp_storage[code] = expires_at
    # 10 мүнөттөн кийин код автоматтык түрдө өчүрүлөт (кодду тазалоо функциясы кошсок болот)
    return {"status": "ok", "message": "OTP generated", "code": code}

@router.post("/verify")
async def verify_otp(body: OtpCode):
    code = body.code
    if code in otp_storage:
        expires_at = otp_storage[code]
        if datetime.now() < expires_at:
            # Код ишенимдүү, аны өчүрөбүз (бир жолу колдонулгандан кийин)
            del otp_storage[code]
            return {"status": "ok", "valid": True}
        else:
            # Коддун мөөнөтү бүткөн
            del otp_storage[code]
            return {"status": "fail", "valid": False, "message": "Code expired"}
    else:
        return {"status": "fail", "valid": False, "message": "Invalid code"}

app.include_router(router)

# Эскертүү: Бул жерде кодду тазалоо функциясы кошсоңуз болот (мисал, ар бир саатта мөөнөтү бүткөн коддорду тазалоо)