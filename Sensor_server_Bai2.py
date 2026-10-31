import asyncio
import json
import random
from datetime import datetime

import aiocoap
import aiocoap.resource as resource


BIND_HOST = "127.0.0.1"
DISPLAY_HOST = "localhost"   
PORT = 5683


BASE_PATH = ("iot", "lab")
DEVICE_IDS = ["sensor01", "sensor02", "sensor03"]

UPDATE_INTERVAL = 3            
TEMPERATURE_RANGE = (20.0, 42.0)   
HUMIDITY_RANGE = (30.0, 80.0)      
CONTENT_FORMAT_JSON = 50       


def now_iso():
    return datetime.now().isoformat(timespec="seconds")


def now_hms():
    return datetime.now().strftime("%H:%M:%S")


class SensorResource(resource.Resource):
    """Mô phỏng 1 thiết bị cảm biến nhiệt độ và độ ẩm."""

    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id
        self.temperature = 0.0
        self.humidity = 0.0
        self.timestamp = ""
        self.get_count = 0

        self._generate_data()  
        self._task = asyncio.create_task(self._update_loop())

    def _generate_data(self):
        self.temperature = round(random.uniform(*TEMPERATURE_RANGE), 1)
        self.humidity = round(random.uniform(*HUMIDITY_RANGE), 1)
        self.timestamp = now_iso()

    async def _update_loop(self):
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)
            self._generate_data()

    async def render_get(self, request):
        self.get_count += 1
        print(f"[{now_hms()}] GET /{'/'.join(BASE_PATH)}/{self.device_id}/data "
              f"(lan thu {self.get_count}) -> "
              f"T={self.temperature} C, H={self.humidity} %")

        data = {
            "device_id": self.device_id,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "timestamp": self.timestamp,
        }
        payload = json.dumps(data).encode("utf-8")
        return aiocoap.Message(
            code=aiocoap.CONTENT,
            payload=payload,
            content_format=CONTENT_FORMAT_JSON,
        )


async def main():
    root = resource.Site()
    for device_id in DEVICE_IDS:
        root.add_resource([*BASE_PATH, device_id, "data"], SensorResource(device_id))

    await aiocoap.Context.create_server_context(root, bind=(BIND_HOST, PORT))

    print(f"CoAP Sensor Server started on port {PORT}")
    for device_id in DEVICE_IDS:
        print(f"Resource: coap://{DISPLAY_HOST}:{PORT}/{'/'.join(BASE_PATH)}/{device_id}/data")
    print("Nhan Ctrl+C de dung server.\n")

    # Giữ server chạy vô hạn
    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSensor server stopped.")