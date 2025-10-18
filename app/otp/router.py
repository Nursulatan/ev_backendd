from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/otp", tags=["OTP"])

class OtpCode(BaseModel):
    code: str

@router.post("/generate")
async def generate_otp():
    # азырынча демо жооп
    return {"status": "ok", "message": "OTP generated", "code": "123456"}

@router.post("/verify")
async def verify_otp(body: OtpCode):
    ok = body.code == "123456"
    return {"status": "ok" if ok else "fail", "valid": ok}