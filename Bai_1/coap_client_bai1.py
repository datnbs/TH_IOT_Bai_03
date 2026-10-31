import asyncio
import aiocoap
from aiocoap.error import Error as CoAPError

# Cấu hình URI và thông tin sinh viên
SERVER_URI = "coap://127.0.0.1:5683/iot/lab/message"
DISPLAY_URI = "coap://localhost:5683/iot/lab/message"
INVALID_URI = "coap://127.0.0.1:5683/iot/lab/unknown_resource"

STUDENT_ID = "B23DCCN171"
STUDENT_NAME = "Le Trung Duc"
TIMEOUT_SECONDS = 5.0


async def send_get(protocol, uri, display_uri=None):
    target_display = display_uri if display_uri else uri
    print("Sending GET request...")
    print(f"URI: {target_display}\n")

    request = aiocoap.Message(code=aiocoap.GET, uri=uri)
    try:
        response = await asyncio.wait_for(
            protocol.request(request).response, timeout=TIMEOUT_SECONDS
        )
        print("Response:")
        print(f"Code: {response.code}")
        print(f"Payload: {response.payload.decode('utf-8')}\n")
        return response
    except asyncio.TimeoutError:
        print(f"[ERROR] Timeout: Server khong phan hoi sau {TIMEOUT_SECONDS} giay.\n")
    except CoAPError as e:
        print(f"[ERROR] Loi ket noi CoAP: {e}\n")
    except Exception as e:
        print(f"[ERROR] Khong the ket noi toi Server: {e}\n")
    return None


async def send_post(protocol, uri, message_text):
    print("Sending POST request...")
    print(f"Payload: {message_text}\n")

    request = aiocoap.Message(
        code=aiocoap.POST,
        uri=uri,
        payload=message_text.encode("utf-8")
    )
    try:
        response = await asyncio.wait_for(
            protocol.request(request).response, timeout=TIMEOUT_SECONDS
        )
        print("Response:")
        print(f"Code: {response.code}")
        print(f"Payload: {response.payload.decode('utf-8')}\n")
        return response
    except asyncio.TimeoutError:
        print(f"[ERROR] Timeout: Server khong phan hoi sau {TIMEOUT_SECONDS} giay.\n")
    except CoAPError as e:
        print(f"[ERROR] Loi ket noi CoAP: {e}\n")
    except Exception as e:
        print(f"[ERROR] Khong the ket noi toi Server: {e}\n")
    return None


async def run_standard_flow(protocol):
    """Chạy kịch bản chuẩn bám sát đầu ra mẫu của đề bài"""
    # 1. Gửi GET lấy thông điệp chào mừng
    await send_get(protocol, SERVER_URI, DISPLAY_URI)

    # 2. Gửi POST chứa thông tin sinh viên
    post_payload = f"Xin chao tu CoAP Client - {STUDENT_ID} - {STUDENT_NAME}"
    await send_post(protocol, SERVER_URI, post_payload)


async def run_extended_flow(protocol):
    """Chạy bổ sung các yêu cầu trong phần Gợi ý mở rộng"""
    print("=== KIEM THU PHAN MO RONG ===")
    
    # 1. Gửi nhiều thông điệp POST liên tiếp
    for i in range(1, 3):
        msg = f"Thong diep lan {i} - {STUDENT_ID} - {STUDENT_NAME}"
        await send_post(protocol, SERVER_URI, msg)

    # 2. Gửi GET lại để kiểm tra Server có trả về thông điệp POST gần nhất không
    print("--- Kiem tra GET lay thong diep POST gan nhat ---")
    await send_get(protocol, SERVER_URI, DISPLAY_URI)

    # 3. Truy cập tài nguyên không tồn tại (4.04 Not Found)
    print("--- Kiem tra truy cap URI khong ton tai ---")
    await send_get(protocol, INVALID_URI)


async def main():
    protocol = await aiocoap.Context.create_client_context()
    try:
        # Chạy luồng chính theo mẫu đề bài
        await run_standard_flow(protocol)

        # Bỏ comment dòng dưới nếu muốn chạy luôn kịch bản mở rộng trong 1 lần chạy:
        # await run_extended_flow(protocol)
    finally:
        await protocol.shutdown()


if __name__ == "__main__":
    asyncio.run(main())