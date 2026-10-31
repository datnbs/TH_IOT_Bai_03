## TH_IOT_Bai_03

## Bài 1: Ứng dụng gửi và nhận thông điệp CoAP cơ bản

### 1. Thông tin cấu hình & Tài nguyên
- **Địa chỉ Server:** `127.0.0.1` (`localhost`)
- **Cổng giao tiếp:** `5683` (UDP)
- **URI Tài nguyên:** `coap://localhost:5683/iot/lab/message`
- **Phương thức hỗ trợ:** `GET`, `POST`

### 2. Cách chạy chương trình
Mở 2 cửa sổ Terminal tại thư mục gốc `CoAP_Lab/`:

**Bước 1: Khởi động CoAP Server**
```bash
python bai1/coap_server_bai1.py
```

**Bước 2: Chạy CoAP Client**
```bash
python bai1/coap_client_bai1.py
```

### 3. Kết quả đạt được
- Khởi tạo thành công CoAP Server lắng nghe trên cổng UDP `5683`.
- Client thực hiện thành công yêu cầu `GET` nhận thông điệp chào mừng (`2.05 Content`) và `POST` gửi thông tin sinh viên (`2.04 Changed`).
- Server ghi nhận đúng payload kèm thời gian thực tế (`HH:MM:SS`).
- **Tính năng mở rộng đã hoàn thiện:**
  - Server tự động lưu trữ thông điệp `POST` mới nhất và trả về trong các lần `GET` kế tiếp.
  - Hỗ trợ gửi nhiều bản tin `POST` liên tiếp.
  - Xử lý truy cập tài nguyên không tồn tại (`4.04 Not Found`).
  - Xử lý ngoại lệ và Timeout (`5.0s`) khi Server ngừng hoạt động.