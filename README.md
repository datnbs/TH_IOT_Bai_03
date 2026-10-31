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
## Bài 3: Mô phỏng hệ thống giám sát và điều khiển đèn thông minh bằng CoAP Observe

### 1. Thông tin cấu hình & Tài nguyên
- **Địa chỉ Server:** `127.0.0.1` (`localhost`)
- **Cổng giao tiếp:** `5683` (UDP)
- **URI Tài nguyên:** `coap://127.0.0.1:5683/iot/lab/light01/status`
- **Mã thiết bị:** `light01`
- **Trạng thái ban đầu:** `OFF`
- **Phương thức hỗ trợ:** `GET`, `PUT`, `Observe`
- **Định dạng dữ liệu:** JSON (`application/json`)

### 2. Cách chạy chương trình
Mở 3 cửa sổ Terminal tại thư mục gốc `CoAP_Lab/`:

**Bước 1: Khởi động Smart Light CoAP Server**
```bash
python bai3/light_server_bai3.py
```

**Bước 2: Khởi động Monitoring Client để đăng ký Observe**
```bash
python bai3/light_monitor_bai3.py
```

**Bước 3: Khởi động Controller Client để điều khiển đèn**
```bash
python bai3/light_controller_bai3.py
```

**Bước 4: Nhập các lệnh điều khiển**
- `ON`: Bật đèn bằng phương thức `PUT`.
- `OFF`: Tắt đèn bằng phương thức `PUT`.
- `STATUS`: Truy vấn trạng thái hiện tại bằng phương thức `GET`.
- `EXIT`: Kết thúc chương trình điều khiển.

### 3. Kết quả đạt được
- Xây dựng CoAP Server mô phỏng thiết bị đèn thông minh `light01`, quản lý trạng thái `ON/OFF`.
- Controller Client hỗ trợ gửi yêu cầu `GET` để truy vấn trạng thái và `PUT` để thay đổi trạng thái đèn.
- Server tiếp nhận và xử lý lệnh điều khiển, trả về mã phản hồi CoAP tương ứng (`2.05 Content`, `2.04 Changed`).
- Dữ liệu trạng thái được trao đổi dưới định dạng JSON với các trường `device_id` và `status`.
- Monitoring Client sử dụng cơ chế **CoAP Observe** để đăng ký theo dõi trạng thái thiết bị.
- Khi trạng thái đèn thay đổi, Server tự động gửi thông báo đến Monitoring Client mà không cần thực hiện `GET` định kỳ.
- Monitoring Client hiển thị mã thiết bị, trạng thái mới và thời điểm nhận thông báo (`HH:MM:SS`).
- **Các chức năng bổ sung:**
  - Kiểm tra và từ chối lệnh điều khiển không hợp lệ.
  - Không gửi thông báo Observe nếu trạng thái đèn không thay đổi.
  - Hỗ trợ nhiều Monitoring Client đăng ký theo dõi cùng một tài nguyên.
  - Xử lý các lỗi giao tiếp cơ bản trong quá trình điều khiển và giám sát.
