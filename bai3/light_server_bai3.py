import asyncio
import json
from aiocoap import Message, Context, Code, resource


class SmartLight(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.status = "OFF"

    async def render_get(self, request):
        data = {"device_id": "light01", "status": self.status}
        return Message(code=Code.CONTENT, payload=json.dumps(data).encode(), content_format=50)

    async def render_put(self, request):
        try:
            data = json.loads(request.payload.decode())
            command = data.get("command")
            if data.get("device_id") != "light01" or command not in ("ON", "OFF"):
                return Message(code=Code.BAD_REQUEST, payload=b"Invalid device or command")
        except (ValueError, UnicodeDecodeError, AttributeError):
            return Message(code=Code.BAD_REQUEST, payload=b"Invalid JSON")

        print(f"PUT request received: device=light01, command={command}")
        if self.status != command:
            old = self.status
            self.status = command
            print(f"Light state changed: {old} -> {command}")
            self.updated_state()
            print(f"Notify observers: {command}")
        else:
            print("Light state unchanged")

        message = "Da bat den light01" if command == "ON" else "Da tat den light01"
        return Message(code=Code.CHANGED, payload=message.encode())

    async def add_observation(self, request, serverobservation):
        print("New Observe registration received")
        await super().add_observation(request, serverobservation)


async def main():
    site = resource.Site()
    site.add_resource(("iot", "lab", "light01", "status"), SmartLight())
    server = await Context.create_server_context(site, bind=("127.0.0.1", 5683))
    print("CoAP Smart Light Server started...")
    print("Resource: /iot/lab/light01/status")
    try:
        await asyncio.Future()
    finally:
        await server.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped")
