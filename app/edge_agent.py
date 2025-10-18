import asyncio
import json
import os
import websockets

BACKEND_WS = os.getenv("BACKEND_WS", "wss://ev-backendd.onrender.com/gateway/ws/car-001")
TOKEN      = os.getenv("GATEWAY_TOKEN", "")  # /gateway/token аркылуу алган

async def handle_command(cmd: dict):
    action = cmd.get("action")
    device = cmd.get("device")
    value  = cmd.get("value")

    print(f"[AGENT] CMD => action={action} device={device} value={value}")

    # ---- Мына ушул жерден сен реал драйверди чакырасың ----
    # CAN мисалы (python-can):
    # import can
    # bus = can.interface.Bus(channel='can0', bustype='socketcan')
    # msg = can.Message(arbitration_id=0x123, data=[0x01, 0x02, 0x03], is_extended_id=False)
    # bus.send(msg)

    # BLE мисалы (bleak):
    # from bleak import BleakClient
    # async with BleakClient("AA:BB:CC:...") as client:
    #     await client.write_gatt_char(UUID, b'\x01\x32')

    # Азырынча симуляция:
    await asyncio.sleep(0.2)
    print("[AGENT] Simulated execution done.")

async def main():
    url = f"{BACKEND_WS}?token={TOKEN}"
    print(f"[AGENT] Connecting to {url}")
    async for ws in websockets.connect(url, ping_interval=20, ping_timeout=20):
        try:
            async for message in ws:
                data = json.loads(message)
                if data.get("type") == "command":
                    await handle_command(data.get("command", {}))
                else:
                    print("[AGENT] Unknown message:", data)
        except websockets.ConnectionClosed:
            print("[AGENT] Disconnected, retrying in 3s...")
            await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
