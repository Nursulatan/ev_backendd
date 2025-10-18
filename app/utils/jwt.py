# app/utils/jwt.py
import time, os, jwt
SECRET = os.getenv("JWT_SECRET", "change-me")

def issue_gateway_token(car_id: str, ttl_sec: int = 3600) -> str:
    now = int(time.time())
    payload = {"car_id": car_id, "iat": now, "exp": now + ttl_sec}
    return jwt.encode(payload, SECRET, algorithm="HS256")

def verify_gateway_token(token: str) -> dict:
    return jwt.decode(token, SECRET, algorithms=["HS256"])
