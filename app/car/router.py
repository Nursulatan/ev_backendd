# app/car/router.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, field_validator
from typing import Optional, Literal

router = APIRouter(prefix="/car", tags=["Car"])

# -------- Allowed vocab --------
AllowedAction = Literal[
    "window_open", "window_close", "window_set",
    "ac_on", "ac_off", "ac_set_temp", "ac_set_fan",
    "trunk_open", "trunk_close",
    "hood_open", "hood_close",
    "sunshade_open", "sunshade_close",
    "music_play", "music_pause", "music_next", "music_prev",
    "volume_set", "volume_up", "volume_down",
    "youtube_open", "youtube_close",
    "nav_set_destination", "seat_heat_set",
]
AllowedDevice = Literal[
    "front_left", "front_right", "rear_left", "rear_right",
    "all", "climate", "media", "trunk", "hood", "sunshade", "seat_driver", "seat_passenger"
]

class CarCommand(BaseModel):
    action: AllowedAction
    device: Optional[AllowedDevice] = None
    value: Optional[float] = None  # % же градус/деңгээл (мисалы 0..100, же 16..30)
    meta: Optional[dict] = None    # кошумча маалымат (мис: address, videoId)

    @field_validator("value")
    @classmethod
    def check_value(cls, v, info):
        if v is None:
            return v
        # коопсуз диапазондор
        try:
            vf = float(v)
        except Exception:
            raise ValueError("value must be a number")
        # жалпы интерпретация: терезе/томбрейлер: 0..100, температура: 16..30, үн: 0..100
        if vf < -100 or vf > 1000:  # жөн эле өтө чоң/терс маанилерге чектөө
            raise ValueError("value is out of allowed range")
        return vf

class ExecResponse(BaseModel):
    ok: bool
    message: str
    applied: Optional[CarCommand] = None

# Опциялык жөнөкөй “админ-ключ” коргоо (кааласаң алып таштайсың)
ADMIN_KEY = ""  # .env'ден жүктөп койсо болот

@router.post("/execute", response_model=ExecResponse)
def execute_command(
    cmd: CarCommand,
    x_admin_key: Optional[str] = Header(default=None, alias="X-Admin-Key")
):
    if ADMIN_KEY and x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # --------- Логика (симуляция) ---------
    # Реал интеграцияда бул жерден унаанын драйверин/ECU API'сын чакырасың:
    #   e.g. can_bus.send(...), ble_driver.set_window(...), vendor_api.post(...)

    # Жөнөкөй текшерүүлөр
    if cmd.action.startswith("window"):
        if cmd.device not in ("front_left", "front_right", "rear_left", "rear_right", "all"):
            raise HTTPException(400, detail="window action requires device (one of door windows or 'all')")
        if cmd.action in ("window_open", "window_set") and cmd.value is not None:
            if not (0 <= float(cmd.value) <= 100):
                raise HTTPException(400, detail="window percent must be 0..100")
    if cmd.action == "ac_set_temp":
        if cmd.value is None or not (16 <= float(cmd.value) <= 30):
            raise HTTPException(400, detail="ac_set_temp requires value in 16..30 C")
    if cmd.action == "volume_set":
        if cmd.value is None or not (0 <= float(cmd.value) <= 100):
            raise HTTPException(400, detail="volume_set requires value in 0..100")

    # Симуляцияланган жооп:
    return ExecResponse(
        ok=True,
        message=f"Executed: action={cmd.action}, device={cmd.device}, value={cmd.value}",
        applied=cmd
    )
