import asyncio
import json
from aiocoap import Context, Message, Code

URI = "coap://127.0.0.1:5683/iot/lab/light01/status"


async def main():
    protocol = await Context.create_client_context()
    try:
        while True:
            command = (await asyncio.to_thread(input, "Nhap lenh (ON/OFF/STATUS/EXIT): ")).strip().upper()
            if command == "EXIT":
                break
            if command not in ("ON", "OFF", "STATUS"):
                print("Lenh khong hop le")
                continue
            try:
                if command == "STATUS":
                    print("Sending GET request...")
                    request = Message(code=Code.GET, uri=URI)
                else:
                    print("Sending PUT request...")
                    payload = json.dumps({"device_id": "light01", "command": command}).encode()
                    request = Message(code=Code.PUT, uri=URI, payload=payload, content_format=50)
                response = await asyncio.wait_for(protocol.request(request).response, timeout=10)
                print("Response Code:", response.code)
                print("Response:", response.payload.decode())
            except (asyncio.TimeoutError, OSError, Exception) as exc:
                print("Loi giao tiep:", exc)
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Controller stopped")
