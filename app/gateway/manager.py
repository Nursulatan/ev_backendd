# app/gateway/manager.py
from typing import Dict
from fastapi import WebSocket

class GatewayRegistry:
    def __init__(self) -> None:
        self._ws_by_car: Dict[str, WebSocket] = {}

    def online(self, car_id: str, ws: WebSocket):
        self._ws_by_car[car_id] = ws

    def offline(self, car_id: str):
        self._ws_by_car.pop(car_id, None)

    def get(self, car_id: str) -> WebSocket | None:
        return self._ws_by_car.get(car_id)

gateway_registry = GatewayRegistry()
