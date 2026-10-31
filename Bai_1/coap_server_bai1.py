import asyncio
from datetime import datetime
import aiocoap
import aiocoap.resource as resource


class MessageResource(resource.Resource):
    def __init__(self):
        super().__init__()
        # Trạng thái mặc định ban đầu theo đúng yêu cầu đề bài
        self.current_message = "Xin chao tu CoAP Server"

    async def render_get(self, request):
        print("\nGET request received: /iot/lab/message")
        
        payload = self.current_message.encode("utf-8")
        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

    async def render_post(self, request):
        incoming_payload = request.payload.decode("utf-8")
        current_time = datetime.now().strftime("%H:%M:%S")

        print("\nPOST request received:")
        print(f"Payload: {incoming_payload}")
        print(f"Time: {current_time}")

        # Mở rộng: Lưu lại thông điệp POST gần nhất cho lần GET tiếp theo
        self.current_message = incoming_payload

        response_payload = "Server da nhan thong diep".encode("utf-8")
        return aiocoap.Message(code=aiocoap.CHANGED, payload=response_payload)


async def main():
    # Khởi tạo cây tài nguyên (Resource Tree)
    root = resource.Site()
    
    # Định nghĩa URI: /iot/lab/message
    root.add_resource(["iot", "lab", "message"], MessageResource())

    # Bind trực tiếp vào 127.0.0.1 cổng 5683 để tránh lỗi IPv6 trên Windows
    await aiocoap.Context.create_server_context(root, bind=("127.0.0.1", 5683))
    print("CoAP Server started on port 5683")

    # Giữ Server chạy liên tục
    try:
        await asyncio.get_running_loop().create_future()
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCoAP Server stopped.")