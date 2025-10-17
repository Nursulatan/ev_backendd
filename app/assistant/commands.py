# app/assistant/commands.py
from __future__ import annotations
import re
from typing import Optional, Dict, Any

# ---------- Helpers

def _to_num(text: str, default: Optional[float] = None) -> Optional[float]:
    """
    Сандан %/°С/уровень сыяктуу нерселерди сууруп чыгат: "30", "30%", "22°", "уровень 2"
    Үтүр-ноктого чыдайт: "22,5".
    """
    m = re.search(r"(?P<num>\d+(?:[.,]\d+)?)", text)
    if not m:
        return default
    return float(m.group("num").replace(",", "."))

def _pct(text: str) -> Optional[int]:
    """
    "%", "половина", "жарымы", "орточо" сыяктуу айтылууларды 0..100 га нормалдаштырат.
    """
    txt = text.lower().strip()
    # Сандык пайыз
    m = re.search(r"(\d+)\s*%?", txt)
    if m:
        v = int(m.group(1))
        return max(0, min(100, v))
    # Сөз менен
    words_50 = {"жарым", "половина", "орточо", "середина", "средне"}
    if any(w in txt for w in words_50):
        return 50
    words_100 = {"толук ач", "полностью", "на всю", "на максимум", "акырынан эмес"}
    if any(w in txt for w in words_100):
        return 100
    words_0 = {"жап", "закрой", "выключи", "өчүр"}
    if any(w in txt for w in words_0):
        return 0
    return None

def _which_window(txt: str) -> str:
    """
    Кайсы терезе: all/front_left/front_right/rear_left/rear_right
    """
    t = txt.lower()
    if any(w in t for w in ("баары", "все", "всё", "всех", "бардык")):
        return "all"
    if any(w in t for w in ("алдыңкы сол", "алдынкы сол", "переднее лев", "водительск")):
        return "front_left"
    if any(w in t for w in ("алдыңкы оң", "алдынкы оң", "переднее прав")):
        return "front_right"
    if any(w in t for w in ("арткы сол", "заднее лев")):
        return "rear_left"
    if any(w in t for w in ("арткы оң", "заднее прав")):
        return "rear_right"
    # эгер көрсөтүлбөсө — бардык
    return "all"

def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


# ---------- Parsers (KG/RU)

def _parse_windows(text: str) -> Optional[Dict[str, Any]]:
    """
    Мисалдар:
      - "сол алдыңкы терезени 30% ач"
      - "все окна закрой"
      - "арткы сол терезени көтөр 20%"
    """
    t = _normalize(text)
    if not any(w in t for w in ("терезе", "окно", "окн")):
        return None

    target = _which_window(t)

    # Ачуу / көтөрүү
    if any(w in t for w in ("ач", "подними", "поднять", "открой", "көтер")):
        val = _pct(t)
        return {
            "type": "command",
            "device": "window",
            "action": "open",
            "target": target,
            "value": val,    # пайыз, None болсо "толук"
            "unit": "percent" if val is not None else None,
            "raw": text,
        }

    # Жапуу / түшүрүү
    if any(w in t for w in ("жап", "закрой", "опусти", "опустить", "түшүр")):
        val = _pct(t)
        if val is None:
            val = 0
        return {
            "type": "command",
            "device": "window",
            "action": "close",
            "target": target,
            "value": val,
            "unit": "percent",
            "raw": text,
        }

    return None


def _parse_climate(text: str) -> Optional[Dict[str, Any]]:
    """
    - "печкени 22ге кой"
    - "кондиционерди күйгүз" / "выключи кондиционер"
    - "абанын ылдамдыгын 3кө кой"
    - "defrost алдыңкыны күйгүз"
    """
    t = _normalize(text)
    if not any(w in t for w in ("печка", "климат", "кондиционер", "кондер", "ac", "аба", "температура", "defrost", "обдув")):
        return None

    # Температура
    if any(w in t for w in ("градус", "°", "температура", "темпу")):
        num = _to_num(t)
        if num is not None:
            return {
                "type": "command",
                "device": "climate",
                "action": "set_temperature",
                "value": num,
                "unit": "celsius",
                "raw": text,
            }

    # AC ON/OFF
    if any(w in t for w in ("күйгүз", "включи", "оңдоп күйгүз", "zapusti")) and any(w in t for w in ("кондиционер", "кондер", "ac")):
        return {
            "type": "command",
            "device": "climate",
            "action": "ac_on",
            "raw": text,
        }
    if any(w in t for w in ("өчүр", "выключи")) and any(w in t for w in ("кондиционер", "кондер", "ac")):
        return {
            "type": "command",
            "device": "climate",
            "action": "ac_off",
            "raw": text,
        }

    # Желдеткич ылдамдыгы (fan)
    if any(w in t for w in ("желдет", "вентил", "аба")) and any(w in t for w in ("ылдам", "скорост", "уров", "деңгээл")):
        lvl = int(_to_num(t, 0) or 0)
        lvl = max(0, min(7, lvl))  # 0..7
        return {
            "type": "command",
            "device": "climate",
            "action": "set_fan_speed",
            "value": lvl,
            "unit": "level",
            "raw": text,
        }

    # Defrost
    if "defrost" in t or "обдув" in t:
        front = any(w in t for w in ("алдыңкы", "передн"))
        rear = any(w in t for w in ("арткы", "задн"))
        if front:
            return {"type": "command", "device": "climate", "action": "defrost_front", "raw": text}
        if rear:
            return {"type": "command", "device": "climate", "action": "defrost_rear", "raw": text}

    return None


def _parse_trunk_shade(text: str) -> Optional[Dict[str, Any]]:
    """
    - "багажникты ач"
    - "багажды жап"
    - "шторканы ач", "шторка закрыть"
    """
    t = _normalize(text)

    if any(w in t for w in ("багаж", "багажник", "trunk")):
        if any(w in t for w in ("ач", "открой")):
            return {"type": "command", "device": "trunk", "action": "open", "raw": text}
        if any(w in t for w in ("жап", "закрой")):
            return {"type": "command", "device": "trunk", "action": "close", "raw": text}

    if any(w in t for w in ("шторка", "шторку", "шторки", "занавес")):
        if any(w in t for w in ("ач", "открой")):
            return {"type": "command", "device": "sunshade", "action": "open", "raw": text}
        if any(w in t for w in ("жап", "закрой")):
            return {"type": "command", "device": "sunshade", "action": "close", "raw": text}

    return None


def _parse_media(text: str) -> Optional[Dict[str, Any]]:
    """
    - "музыканы күйгүз/өчүр", "поставь паузу", "следующий трек"
    - "громкость 50%", "күчөт үнүн 30га"
    - "ютуб ач", "YouTube'дан Кино издегиле"
    """
    t = _normalize(text)

    # Volume
    if any(w in t for w in ("громк", "үнүн", "volume")):
        v = _pct(t)
        if v is None:
            # "күчөт", "азайт" түрү
            if any(w in t for w in ("күчөт", "увелич", "прибав")):
                return {"type": "command", "device": "media", "action": "volume_up", "raw": text}
            if any(w in t for w in ("азайт", "уменьш", "убав")):
                return {"type": "command", "device": "media", "action": "volume_down", "raw": text}
        else:
            return {"type": "command", "device": "media", "action": "set_volume", "value": v, "unit": "percent", "raw": text}

    # Playback
    if any(w in t for w in ("күйгүз", "включи", "play")) and "музык" in t:
        return {"type": "command", "device": "media", "action": "play", "raw": text}
    if any(w in t for w in ("өчүр", "выключи", "pause", "пауз")) and "музык" in t:
        return {"type": "command", "device": "media", "action": "pause", "raw": text}
    if any(w in t for w in ("кийинки", "следующ", "next", "алмаштыр")):
        return {"type": "command", "device": "media", "action": "next", "raw": text}
    if any(w in t for w in ("мурунку", "предыдущ", "previous")):
        return {"type": "command", "device": "media", "action": "prev", "raw": text}

    # YouTube
    if "youtube" in t or "ютуб" in t:
        # "ютубтан ..." издегиле
        m = re.search(r"(youtube|ютуб).*?(изде|найди|поиск|search)\s+(?P<q>.+)$", t)
        if m:
            return {"type": "command", "device": "youtube", "action": "search", "query": m.group("q"), "raw": text}
        return {"type": "command", "device": "youtube", "action": "open", "raw": text}

    return None


# ---------- Public API

def handle_local_command(text: str) -> Optional[Dict[str, Any]]:
    """
    Негизги кирүү чекити. Команда таанылса — структураланган dict,
    болбосо None кайтарат.
    Порядок: window → climate → trunk/shade → media
    """
    parsers = (_parse_windows, _parse_climate, _parse_trunk_shade, _parse_media)
    for p in parsers:
        got = p(text)
        if got:
            return got
    return None
