from fastapi import APIRouter

router = APIRouter(prefix="/otp", tags=["otp"])

@router.get("/")
def get_otp_status():
    return {"status": "OTP service ready"}
