import random, time
from fastapi import APIRouter, Depends, HTTPException
from .deps import get_current_admin
from .config import settings
try:
    import redis
    r = redis.from_url(settings.REDIS_URL, decode_responses=True); r.ping(); use_redis=True
except Exception:
    r=None; use_redis=False
_mem = {"code": None, "exp": 0}
router = APIRouter(prefix="/otp", tags=["otp"])

@router.post("/generate")
def gen(_: dict = Depends(get_current_admin)):
    code = f"{random.randint(0,999999):06d}"
    if use_redis and r: r.set("active_code", code, ex=settings.OTP_TTL_SECONDS)
    else: _mem.update(code=code, exp=time.time()+settings.OTP_TTL_SECONDS)
    return {"code": code, "ttl": settings.OTP_TTL_SECONDS, "backend": "redis" if use_redis else "memory"}

@router.post("/verify")
def verify(body: dict):
    code = body.get("code")
    if not code: raise HTTPException(status_code=400, detail="Code required")
    if use_redis and r:
        cur = r.get("active_code"); 
        if cur and cur==code: r.delete("active_code"); return {"ok": True}
        raise HTTPException(status_code=401, detail="Invalid or expired code")
    else:
        if _mem["code"] and time.time()<=_mem["exp"] and _mem["code"]==code:
            _mem.update(code=None, exp=0); return {"ok": True}
        raise HTTPException(status_code=401, detail="Invalid or expired code")
