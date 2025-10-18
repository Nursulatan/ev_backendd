# app/gateway/token_router.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from app.utils.jwt import issue_gateway_token

router = APIRouter(prefix="/gateway", tags=["Gateway"])

class TokenOut(BaseModel):
    car_id: str
    token: str

@router.post("/token", response_model=TokenOut)
def get_token(car_id: str, x_admin_key: str | None = Header(default=None, alias="X-Admin-Key")):
    # кааласаң бул жерди ADMIN_KEY менен коргойсуң
    token = issue_gateway_token(car_id, ttl_sec=7*24*3600)
    return TokenOut(car_id=car_id, token=token)
