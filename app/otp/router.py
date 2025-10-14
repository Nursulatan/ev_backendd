from fastapi import APIRouter

router = APIRouter(prefix="/otp", tags=["otp"])

@router.post("/generate")
async def generate_otp():
    return {"status": "ok", "message": "OTP generated"}

@router.post("/verify")
async def verify_otp():
    return {"status": "ok", "message": "OTP verified"}
