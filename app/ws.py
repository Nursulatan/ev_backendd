from fastapi import APIRouter, WebSocket
from .ev_driver import ev
from .ai_nlu import interpret
router = APIRouter()
@router.websocket('/ws/assistant')
async def ws_entry(ws:WebSocket):
    await ws.accept()
    while True:
        data = await ws.receive_json()
        if data.get('type')=='asr_text':
            intent,slots=interpret(data['text'], data.get('lang','ru'))
            res=ev.execute({'intent':intent,**slots}); await ws.send_json({'type':'result','result':res})
        elif data.get('type')=='macro':
            for cmd in data.get('commands',[]): ev.execute(cmd)
            await ws.send_json({'type':'result','result':{'status':'ok'}})
