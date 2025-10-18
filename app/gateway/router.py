# app/gateway/router.py
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from app.gateway.manager import gateway_registry
from app.utils.jwt import verify_gateway_token  # төмөндө кошобуз

router = APIRouter(prefix="/gateway", tags=["Gateway"])

@router.websocket("/ws/{car_id}")
async def gateway_ws(ws: WebSocket, car_id: str, token: str = Query(...)):
    # коопсуздук: токен текшер
    payload = verify_gateway_token(token)  # car_id текшерүү (payload["car_id"] == car_id)
    if payload.get("car_id") != car_id:
        await ws.close(code=4401)
        return

    await ws.accept()
    gateway_registry.online(car_id, ws)
    try:
        while True:
            # агенттен да билдирүү келиши мүмкүн (телеметрия, ack ж.б.)
            msg = await ws.receive_text()
            # кааласаң логго жазып койсоң болот
            # print(f"[{car_id}] -> {msg}")
    except WebSocketDisconnect:
        gateway_registry.offline(car_id)
