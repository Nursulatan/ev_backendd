# app/assistant/router.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import re

router = APIRouter(prefix="/assistant", tags=["Assistant"])

class HandleIn(BaseModel):
    text: str
    lang: Optional[str] = None   # "ky-KG" | "ru-RU" (кааласаң бош калса — автоматтык)
    name: Optional[str] = None   # "ассистент" | "унаа" (болбосо дагы иштейт)

class HandleOut(BaseModel):
    ok: bool
    command: Optional[Dict[str, Any]] = None
    speech: str

# -------- utilities --------
def _detect_lang(s: str) -> str:
    s_low = s.lower()
    if re.search(r"[ңөү]", s_low) or re.search(r"[ҢӨҮ]", s):
        return "ky-KG"
    return "ru-RU"

def _to_number(token: str) -> Optional[float]:
    token = token.replace(",", ".")
    try:
        return float(re.sub(r"[^\d\.]", "", token))
    except Exception:
        return None

def _percent_in_text(s: str) -> Optional[float]:
    # 50%, 50 пайыз, 50 процентов
    m = re.search(r"(\d+)\s*(%|пайыз|процент)", s, flags=re.I)
    if m:
        return float(m.group(1))
    # "жарым" (50), "полностью" (100), "толук" (100), "азайтып/бир аз" (25)
    if re.search(r"\bжарым\b", s, flags=re.I): return 50.0
    if re.search(r"\b(толук|полностью)\b", s, flags=re.I): return 100.0
    return None

def _temp_in_text(s: str) -> Optional[float]:
    # 21°, 21 градус
    m = re.search(r"(\d{1,2})\s*(°|градус)", s, flags=re.I)
    if m: return float(m.group(1))
    # мис: "температураны 22 кыл"
    m2 = re.search(r"температура\D+(\d{1,2})", s, flags=re.I)
    if m2: return float(m2.group(1))
    return None

def _volume_in_text(s: str) -> Optional[float]:
    # 0..100
    m = re.search(r"(үнү|громкост[ьи])\D+(\d{1,3})", s, flags=re.I)
    if m:
        v = float(m.group(2))
        return max(0.0, min(100.0, v))
    p = _percent_in_text(s)
    if p is not None:
        return max(0.0, min(100.0, p))
    return None

def _which_window(s: str) -> str:
    s = s.lower()
    # default 'all' if not specified
    if re.search(r"(алдыңкы|передн).*сол|front.*left|лев(ая|ый).*перед", s): return "front_left"
    if re.search(r"(алдыңкы|передн).*оң|front.*right|прав(ая|ый).*перед", s): return "front_right"
    if re.search(r"(арт(кы|кы)|задн).*сол|rear.*left|лев(ая|ый).*зад", s): return "rear_left"
    if re.search(r"(арт(кы|кы)|задн).*оң|rear.*right|прав(ая|ый).*зад", s): return "rear_right"
    if re.search(r"(бардыгы|все|всё|всё окна|все окна|баары)", s): return "all"
    return "all"

# -------- main parser --------
def parse_command(text: str) -> Optional[Dict[str, Any]]:
    s = re.sub(r"\s+", " ", text.strip().lower())

    # WINDOWS
    if re.search(r"(терезе|окно)", s):
        device = _which_window(s)
        if re.search(r"(жап|закрой|закрыть)", s):
            return {"action":"window_close","device":device}
        if re.search(r"(ач|откр(ой|ыть))", s):
            p = _percent_in_text(s)
            if p is not None:
                return {"action":"window_set","device":device,"value":max(0,min(100,p))}
            return {"action":"window_open","device":device}
        p = _percent_in_text(s)
        if p is not None:
            return {"action":"window_set","device":device,"value":max(0,min(100,p))}

    # CLIMATE
    if re.search(r"(печка|климат|кондиционер|ауа|аба)", s):
        if re.search(r"(жак|включи|вкл)", s):
            return {"action":"ac_on","device":"climate"}
        if re.search(r"(өчүр|выключи|выкл)", s):
            return {"action":"ac_off","device":"climate"}
        t = _temp_in_text(s)
        if t is not None:
            return {"action":"ac_set_temp","device":"climate","value":max(16,min(30,t))}
        # желдеткич/обдув 0..100
        if re.search(r"(фан|желе|обдув|скорост[ьи])", s):
            p = _percent_in_text(s)
            if p is not None:
                return {"action":"ac_set_fan","device":"climate","value":max(0,min(100,p))}

    # TRUNK / HOOD / SUNSHADE
    if re.search(r"(багаж|багажник)", s):
        if re.search(r"(ач|откр)", s): return {"action":"trunk_open","device":"trunk"}
        if re.search(r"(жап|закр)", s): return {"action":"trunk_close","device":"trunk"}

    if re.search(r"(капот|капот)", s):
        if re.search(r"(ач|откр)", s): return {"action":"hood_open","device":"hood"}
        if re.search(r"(жап|закр)", s): return {"action":"hood_close","device":"hood"}

    if re.search(r"(шторка|штора|люк)", s):
        if re.search(r"(ач|откр)", s): return {"action":"sunshade_open","device":"sunshade"}
        if re.search(r"(жап|закр)", s): return {"action":"sunshade_close","device":"sunshade"}

    # MEDIA / MUSIC
    if re.search(r"(муз|music|плей|ойно|проигр|play)", s):
        return {"action":"music_play","device":"media"}
    if re.search(r"(токтот|пауза|pause|останов)", s):
        return {"action":"music_pause","device":"media"}
    if re.search(r"(кийинки|следующ|next)", s):
        return {"action":"music_next","device":"media"}
    if re.search(r"(мурунку|предыдущ|prev)", s):
        return {"action":"music_prev","device":"media"}

    # VOLUME
    if re.search(r"(үн|громкост[ьи])", s):
        v = _volume_in_text(s)
        if v is not None:
            return {"action":"volume_set","device":"media","value":max(0,min(100,v))}
        if re.search(r"(көбөйт|увелич|громче|\+)", s):
            return {"action":"volume_up","device":"media"}
        if re.search(r"(азаайт|уменьш|тише|-)", s):
            return {"action":"volume_down","device":"media"}

    # YOUTUBE
    if re.search(r"(youtube|ютуб)", s):
        if re.search(r"(ач|откр|запусти|включи)", s):
            return {"action":"youtube_open","device":"media"}
        if re.search(r"(жап|закр|выключи|останови)", s):
            return {"action":"youtube_close","device":"media"}

    # SEAT HEAT
    if re.search(r"(отургуч|сиденье).*(жылуу|подогрев)", s):
        lvl = _percent_in_text(s)
        if lvl is None:
            lvl = 50.0
        seat = "seat_driver" if re.search(r"(айдооч|водител)", s) else "seat_passenger" if re.search(r"(жолоч|пассажир)", s) else "seat_driver"
        return {"action":"seat_heat_set","device":seat,"value":max(0,min(100,lvl))}

    # Навигация (жөнөкөй демо)
    if re.search(r"(бар|поехали|навигац|маршрут)", s):
        # адрести meta'га сактайбыз (чыныгы парсерде толугураак NLP)
        m = re.search(r"(бар|в|к)\s+(.+)$", s)
        address = m.group(2).strip() if m else ""
        return {"action":"nav_set_destination","device":"media","meta":{"address":address}}

    return None

def _confirm_speech(cmd: Dict[str, Any], lang: str) -> str:
    act = cmd.get("action","")
    dev = cmd.get("device","")
    val = cmd.get("value", None)

    if lang == "ky-KG":
        if act == "window_close": return "Ок, терезени жаптым."
        if act == "window_open":  return "Ок, терезени ачтым."
        if act == "window_set":   return f"Ок, терезени {int(val)}% кылдым."
        if act == "ac_on":        return "Климат системасын күйгүздүм."
        if act == "ac_off":       return "Климат системасын өчүрдүм."
        if act == "ac_set_temp":  return f"Температураны {int(val)}° кылдым."
        if act == "ac_set_fan":   return f"Желдеткичти {int(val)}% кылдым."
        if act == "trunk_open":   return "Багажник ачылды."
        if act == "trunk_close":  return "Багажник жабылды."
        if act == "hood_open":    return "Капот ачылды."
        if act == "hood_close":   return "Капот жабылды."
        if act == "sunshade_open":return "Шторканы ачтым."
        if act == "sunshade_close":return "Шторканы жаптым."
        if act == "music_play":   return "Музыка ойной баштады."
        if act == "music_pause":  return "Музыка токтотулду."
        if act == "music_next":   return "Кийинки трек."
        if act == "music_prev":   return "Мурунку трек."
        if act == "volume_set":   return f"Үн деңгээли {int(val)}%."
        if act == "volume_up":    return "Үнүн көбөйттүм."
        if act == "volume_down":  return "Үнүн азайттым."
        if act == "youtube_open": return "YouTube ачылды."
        if act == "youtube_close":return "YouTube жабылды."
        if act == "seat_heat_set":return f"Отургучтун жылытуусу {int(val)}%."
        if act == "nav_set_destination": return "Маршрут орнотулду."
        return "Макул."
    else:
        if act == "window_close": return "Окна закрыла."
        if act == "window_open":  return "Окна открыла."
        if act == "window_set":   return f"Окна на {int(val)}%."
        if act == "ac_on":        return "Климат включен."
        if act == "ac_off":       return "Климат выключен."
        if act == "ac_set_temp":  return f"Температура {int(val)}°."
        if act == "ac_set_fan":   return f"Вентилятор {int(val)}%."
        if act == "trunk_open":   return "Багажник открыт."
        if act == "trunk_close":  return "Багажник закрыт."
        if act == "hood_open":    return "Капот открыт."
        if act == "hood_close":   return "Капот закрыт."
        if act == "sunshade_open":return "Шторка открыта."
        if act == "sunshade_close":return "Шторка закрыта."
        if act == "music_play":   return "Музыка включена."
        if act == "music_pause":  return "Музыка на паузе."
        if act == "music_next":   return "Следующий трек."
        if act == "music_prev":   return "Предыдущий трек."
        if act == "volume_set":   return f"Громкость {int(val)}%."
        if act == "volume_up":    return "Сделала громче."
        if act == "volume_down":  return "Сделала тише."
        if act == "youtube_open": return "YouTube открыт."
        if act == "youtube_close":return "YouTube закрыт."
        if act == "seat_heat_set":return f"Подогрев сиденья {int(val)}%."
        if act == "nav_set_destination": return "Маршрут установлен."
        return "Хорошо."

@router.post("/handle", response_model=HandleOut)
def handle_command(body: HandleIn):
    text = (body.text or "").strip()
    if not text:
        lang = body.lang or "ky-KG"
        return HandleOut(ok=False, command=None,
                         speech="Кайра айтыңызчы." if lang=="ky-KG" else "Повторите, пожалуйста.")
    # тил
    lang = body.lang or _detect_lang(text)
    # ат айтылса алып салабыз (фронт да кесет, бул жерде кошумча)
    if body.name:
        name = body.name.strip().lower()
        if text.lower().startswith(name):
            text = text[len(name):].lstrip()

    cmd = parse_command(text)
    if not cmd:
        # түшүнбөсө кыска жооп
        return HandleOut(
            ok=False, command=None,
            speech="Түшүнгөн жокмун, кайра айтыңызчы." if lang=="ky-KG"
                   else "Не поняла, повторите, пожалуйста."
        )

    return HandleOut(ok=True, command=cmd, speech=_confirm_speech(cmd, lang))
