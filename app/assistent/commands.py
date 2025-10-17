# app/assistant/commands.py
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any

# ---------- Helpers

def _to_num(text: str, default: Optional[float]=None) -> Optional[float]:
    m = re.search(r"(-?\d+(?:[.,]\d+)?)", text)
    if not m:
        return default
    return float(m.group(1).replace(",", "."))

def _pct(text: str) -> Optional[int]:
    """Киргизилген тексттен % табат: '50%', '50', 'на 50', 'жарым', 'полностью'."""
    t = text.lower()
    if "полностью" in t or "толук" in t:
        return 100
    if "жарым" in t or "половин" in t:
        return 50
    n = _to_num(t)
    if n is None:
        return None
    if n <= 1 and ("." in t or "," in t):  # 0.3 -> 30%
        return int(round(n * 100))
    return int(round(n))

def _level(text: str) -> Optional[int]:
    """Деңгээл (1..10). 'макс'/'min' да түшүнөт."""
    t = text.lower()
    if "макс" in t or "max" in t:
        return 10
    if "мин" in t or "min" in t:
        return 1
    n = _to_num(t)
    if n is None:
        return None
    return max(1, min(int(round(n)), 10))

def _temp(text: str) -> Optional[float]:
    """Температура °C."""
    n = _to_num(text)
    if n is None:
        return None
    # Эгер F деп айтылса, Цельсийге айлант
    if re.search(r"\b(f|фарен|fahren)", text, re.I):
        n = (n - 32) * 5/9
    return round(n, 1)

def _which_window(t: str) -> str:
    if re.search(r"(алдың|передн).*(сол|лев)", t): return "front_left"
    if re.search(r"(алдың|передн).*(оң|прав)", t):  return "front_right"
    if re.search(r"(арт|задн).*(сол|лев)", t):     return "rear_left"
    if re.search(r"(арт|задн).*(оң|прав)", t):     return "rear_right"
    if re.search(r"(арт|задн)", t):                return "rear"
    if re.search(r"(алдың|передн)", t):            return "front"
    return "all"

# ---------- Ответ структурасы

@dataclass
class CommandResult:
    type: str
    action: str
    target: str = "default"
    value: Optional[Any] = None
    unit: Optional[str] = None
    say: Optional[str] = None

    def dict(self) -> Dict[str, Any]:
        d = {
            "type": self.type,
            "action": self.action,
            "target": self.target,
        }
        if self.value is not None: d["value"] = self.value
        if self.unit  is not None: d["unit"]  = self.unit
        if self.say   is not None: d["say"]   = self.say
        return d

# ---------- Негизги парсер

def handle_local_command(text: str) -> Optional[Dict[str, Any]]:
    """
    Команданы текшерет. Тапса — машинанын иш-аракетине ылайык структура кайтарат.
    Таппаса — None.
    KG + RU аралаш жакшы иштейт.
    """
    t = text.lower().strip()

    # --- WINDOWS
    if re.search(r"(терезе|окн|стекл)", t):
        targ = _which_window(t)
        if re.search(r"(ач|откр|подн[яе])", t):
            p = _pct(t)
            if p is not None:
                return CommandResult("window", "set", targ, p, "%", f"Терезе {p}%").dict()
            return CommandResult("window", "open", targ, say="Терезе ачылды").dict()
        if re.search(r"(жап|закр|опуск)", t):
            p = _pct(t)
            if p is not None:
                return CommandResult("window", "set", targ, p, "%", f"Терезе {p}%").dict()
            return CommandResult("window", "close", targ, say="Терезе жабылды").dict()
        if re.search(r"(вент|аз[ ]ач|приотк)", t):
            return CommandResult("window", "set", targ, 20, "%", "Терезе 20%").dict()

    # --- SUNROOF / ШТОРКА
    if re.search(r"(люк|сунруф|шторк|пердел|штор|shade)", t):
        typ = "sunroof" if re.search(r"(люк|сунруф)", t) else "shade"
        if re.search(r"(ач|откр)", t):
            p = _pct(t) or 100
            return CommandResult(typ, "set", "all", p, "%", f"{typ} {p}%").dict()
        if re.search(r"(жап|закр)", t):
            return CommandResult(typ, "set", "all", 0, "%", f"{typ} жабылды").dict()
        p = _pct(t)
        if p is not None:
            return CommandResult(typ, "set", "all", p, "%", f"{typ} {p}%").dict()

    # --- TRUNK / FRUNK
    if re.search(r"(багаж|багажник|trunk|жүк|фрунк|капот)", t):
        target = "frunk" if re.search(r"(фрунк|капот|frunk)", t) else "trunk"
        if re.search(r"(ач|откр)", t):
            return CommandResult("trunk", "open", target, say=f"{target} ачылды").dict()
        if re.search(r"(жап|закр)", t):
            return CommandResult("trunk", "close", target, say=f"{target} жабылды").dict()

    # --- CLIMATE: AC/HEAT/TEMP/FAN/MODE/RECIRC/DEFROST
    if re.search(r"(климат|печк|отопл|тепл|грейт|обогрев|кондиц|ac|кондёр|муздат|холод)", t):
        # AC On/Off
        if re.search(r"(ac|кондиц|кондёр|муздат|холод)", t):
            if re.search(r"(вкл|күй|on)", t):  return CommandResult("climate","on","ac",say="AC күйдү").dict()
            if re.search(r"(выкл|өч|off)", t): return CommandResult("climate","off","ac",say="AC өчтү").dict()
        # Temperature
        if re.search(r"(темпер|жылуу|сууук|hot|cold)", t):
            temp = _temp(t)
            if temp is not None: return CommandResult("climate","set","temp",temp,"°C",f"Температура {temp}°C").dict()
        # Fan speed
        if re.search(r"(вентил|желдет|fan|обдув|скорост)", t):
            lvl = _level(t)
            if lvl is not None: return CommandResult("climate","set","fan",lvl,"level",f"Вентилятор {lvl}/10").dict()
        # Modes
        if re.search(r"(авто|auto)", t):
            return CommandResult("climate","set","mode","auto",say="Климат AUTO").dict()
        if re.search(r"(стекл|лобов|defrost|обдув стекл)", t):
            return CommandResult("climate","set","mode","defrost",say="Алдыңкы айнекке жылуу аба").dict()
        if re.search(r"(ног|аяк|feet|floor)", t):
            return CommandResult("climate","set","mode","feet",say="Аяк тарабына аба").dict()
        if re.search(r"(лицо|face|центр|централ)", t):
            return CommandResult("climate","set","mode","face",say="Алдыңкы панелге аба").dict()
        # Recirculation
        if re.search(r"(рецирк|внутр|сырт|наруж)", t):
            if re.search(r"(внутр|ичк|рецирк)", t):
                return CommandResult("climate","set","recirc","inside",say="Ички аба айландыруу").dict()
            else:
                return CommandResult("climate","set","recirc","outside",say="Сырттан аба кирсин").dict()

    # --- SEATS HEAT/COOL + HEATED WHEEL
    if re.search(r"(кресл|сиден|отопл сиден|подогрев сиден|орундук)", t):
        lvl = _level(t) or (10 if re.search(r"(макс|max)", t) else 3)
        seat = "driver" if re.search(r"(водит|айдоочу|driver)", t) else ("passenger" if re.search(r"(пассаж|жолокчу)", t) else "front")
        if re.search(r"(охлажд|вентиляц|муздат)", t):
            return CommandResult("seat","set","cool_"+seat,lvl,"level",f"Орундук муздатуу {lvl}/10").dict()
        return CommandResult("seat","set","heat_"+seat,lvl,"level",f"Орундук жылытуу {lvl}/10").dict()

    if re.search(r"(рул|баран|подогрев руля|жылы руль)", t):
        if re.search(r"(вкл|күй|on)", t):  return CommandResult("steering","on","heat",say="Руль жылытуу күйдү").dict()
        if re.search(r"(выкл|өч|off)", t): return CommandResult("steering","off","heat",say="Руль жылытуу өчтү").dict()

    # --- LIGHTS / WIPERS
    if re.search(r"(фара|жарык|свет)", t):
        if re.search(r"(вкл|күй)", t):  return CommandResult("lights","on","head",say="Фаралар күйдү").dict()
        if re.search(r"(выкл|өч)", t): return CommandResult("lights","off","head",say="Фаралар өчтү").dict()
        if re.search(r"(дальн|алый|high)", t): return CommandResult("lights","set","beam","high",say="Дальний").dict()
        if re.search(r"(ближ|жакын|low)", t):  return CommandResult("lights","set","beam","low", say="Ближний").dict()

    if re.search(r"(дворник|шыбырт|wiper|щетк)", t):
        if re.search(r"(вкл|күй)", t):  return CommandResult("wiper","on","auto",say="Дворник AUTO").dict()
        if re.search(r"(выкл|өч)", t): return CommandResult("wiper","off","all",say="Дворник өчтү").dict()
        lvl = _level(t)
        if lvl: return CommandResult("wiper","set","speed",lvl,"level",f"Дворник {lvl}/10").dict()

    # --- MEDIA: play/pause/next/prev, source
    if re.search(r"(музыка|music|аудио|spotify|ютуб|youtube|радио|media|треκ|песня)", t):
        # Source
        if re.search(r"(spotify)", t): return CommandResult("media","set","source","spotify",say="Spotify").dict()
        if re.search(r"(youtube|ютуб)", t): return CommandResult("media","set","source","youtube",say="YouTube").dict()
        if re.search(r"(радио|fm|am)", t): return CommandResult("media","set","source","radio",say="Радио").dict()

        # Transport
        if re.search(r"(пауза|pause|токтоп тур|стоп)", t):
            return CommandResult("media","pause","current",say="Пауза").dict()
        if re.search(r"(плей|ойнот|play|продолж)", t):
            return CommandResult("media","play","current",say="Ойноп жатат").dict()
        if re.search(r"(кийинки|след|next|->)", t):
            return CommandResult("media","next","track",say="Кийинки трек").dict()
        if re.search(r"(мурунку|пред|prev|<-)", t):
            return CommandResult("media","prev","track",say="Мурунку трек").dict()

    # --- VOLUME
    if re.search(r"(громкост|үн|volume|звук)", t):
        if re.search(r"(мьют|тихий|mute)", t):
            return CommandResult("volume","set","master",0,"%", "Үн өчүрүлдү").dict()
        if re.search(r"(увелич|көбөйт|добав|gains|\+|прибав)", t):
            step = _pct(t) or 10
            return CommandResult("volume","change","master",+step,"%", f"Үн +{step}%").dict()
        if re.search(r"(уменьш|азайт|пониз|-|убав)", t):
            step = _pct(t) or 10
            return CommandResult("volume","change","master",-step,"%", f"Үн -{step}%").dict()
        p = _pct(t)
        if p is not None:
            return CommandResult("volume","set","master",p,"%", f"Үн {p}%").dict()

    # --- NAV / YOUTUBE URL
    if re.search(r"(навигац|карта|map|маршрут)", t):
        return CommandResult("nav","open","maps",say="Навигация ачылды").dict()
    if m := re.search(r"(https?://\S+)", t):
        url = m.group(1)
        if "youtube.com" in url or "youtu.be" in url:
            return CommandResult("media","play","youtube_url",url,None,"YouTube ойнотууда").dict()
        return CommandResult("system","open_url","browser",url,None,"URL ачылды").dict()

    # --- CHARGE
    if re.search(r"(заряд|charge|заряж)", t):
        if re.search(r"(нач|старт|start|вкл|күй)", t):  return CommandResult("charge","start","now",say="Заряд башталды").dict()
        if re.search(r"(стоп|өч|выкл)", t):            return CommandResult("charge","stop","now",say="Заряд токтоду").dict()
        if re.search(r"(лимит|огран|до)", t):
            p = _pct(t) or 80
            return CommandResult("charge","set","limit",p,"%",f"Чектөө {p}%").dict()
        if re.search(r"(пор|люч|порт)", t):
            if re.search(r"(откр|ач)", t): return CommandResult("charge","open","port",say="Порт ачылды").dict()
            if re.search(r"(закр|жап)", t): return CommandResult("charge","close","port",say="Порт жабылды").dict()

    # --- SYSTEM MISC
    if re.search(r"(авар|аварийк|hazard|аварийные)", t):
        if re.search(r"(вкл|күй)", t):  return CommandResult("system","on","hazard",say="Аварийка күйдү").dict()
        if re.search(r"(выкл|өч)", t): return CommandResult("system","off","hazard",say="Аварийка өчтү").dict()

    # Тапкан жок
    return None
