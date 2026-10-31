import asyncio
import json
from datetime import datetime
from aiocoap import Context, Message, Code

URI = "coap://127.0.0.1:5683/iot/lab/light01/status"


async def main():
    protocol = await Context.create_client_context()
    request = Message(code=Code.GET, uri=URI, observe=0)
    requester = protocol.request(request)
    first = True

    def display(response):
        nonlocal first
        try:
            data = json.loads(response.payload.decode())
            print(f"\n[{datetime.now():%H:%M:%S}] {'Initial State' if first else 'State Updated'}")
            print("Device:", data["device_id"])
            print("Status:", data["status"])
            first = False
        except (ValueError, KeyError, UnicodeDecodeError) as exc:
            print("Invalid response:", exc)

    try:
        print("Registering CoAP Observe...")
        initial = await asyncio.wait_for(requester.response, timeout=10)
        if not initial.code.is_successful():
            print("Observe failed:", initial.code)
            return
        if requester.observation is None:
            print("Server did not accept Observe")
            return
        print("Observe registration successful")
        display(initial)
        requester.observation.register_callback(display)
        requester.observation.register_errback(lambda error: print("Observe error:", error))
        await asyncio.Future()
    finally:
        if requester.observation is not None:
            requester.observation.cancel()
        await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Monitoring stopped")
