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
## Bài 2: Mô phỏng cảm biến nhiệt độ và độ ẩm bằng CoAP

### 1. Thông tin cấu hình & Tài nguyên

* Địa chỉ Server: `127.0.0.1` (`localhost`)
* Cổng giao tiếp: `5683` (UDP)
* URI Tài nguyên (mỗi cảm biến một URI):
  * `coap://localhost:5683/iot/lab/sensor01/data`
  * `coap://localhost:5683/iot/lab/sensor02/data`
  * `coap://localhost:5683/iot/lab/sensor03/data`
* Phương thức hỗ trợ: `GET`
* Định dạng dữ liệu: JSON, Content-Format `application/json` (mã `50`)
* Chu kỳ cập nhật dữ liệu cảm biến: `3` giây (nhiệt độ `20.0 – 42.0 °C`, độ ẩm `30.0 – 80.0 %`)
* Payload trả về:

```json
{
  "device_id": "sensor01",
  "temperature": 28.5,
  "humidity": 65.2,
  "timestamp": "2026-10-31T10:20:03"
}
```

### 2. Cách chạy chương trình

Mở 2 cửa sổ Terminal tại thư mục gốc `CoAP_Lab/`:

Bước 1: Khởi động Sensor CoAP Server

```
python Sensor_Server_Bai2.py
```

Bước 2: Chạy Monitoring CoAP Client

```
python Monitor_Client_Bai2.py
```

Các tùy chọn của Client:

```
# Chọn mã thiết bị cần giám sát (mặc định: sensor01)
python Monitor_Client_Bai2.py -d sensor02
python Monitor_Client_Bai2.py -d sensor01 sensor03

# Đổi chu kỳ GET (giây) hoặc định dạng file log (csv | json | none)
python Monitor_Client_Bai2.py --interval 3 --log-format json
```

Nhấn `Ctrl+C` để dừng Client; chương trình sẽ in bảng thống kê trước khi thoát.

### 3. Kết quả đạt được

* Khởi tạo thành công Sensor CoAP Server lắng nghe trên cổng UDP `5683`, cung cấp tài nguyên cảm biến qua URI.
* Dữ liệu nhiệt độ, độ ẩm được sinh ngẫu nhiên và tự động cập nhật sau mỗi `3` giây; `GET` luôn trả về giá trị mới nhất.
* Payload trả về đúng định dạng JSON với Content-Format `application/json`.
* Client gửi `GET` định kỳ mỗi `3` giây, phân tích JSON và hiển thị: mã thiết bị, nhiệt độ, độ ẩm, thời điểm nhận (`HH:MM:SS`).
* Cảnh báo hoạt động đúng điều kiện:
  * Nhiệt độ `> 35 °C`: `CANH BAO: Nhiet do cao`
  * Độ ẩm `< 40 %`: `CANH BAO: Do am thap`
  * Ngược lại: `Trang thai: Binh thuong`
* Client giám sát liên tục cho đến khi nhấn `Ctrl+C`.
* Xử lý lỗi: Timeout (`5.0s`) và lỗi kết nối khi Server ngừng hoạt động (Client không bị dừng, tiếp tục thử lại ở chu kỳ sau); hiển thị `4.04 Not Found` khi truy cập mã thiết bị không tồn tại.
* Tính năng mở rộng đã hoàn thiện:
  * Bổ sung trường `timestamp` trong JSON.
  * Mô phỏng 3 cảm biến độc lập: `sensor01`, `sensor02`, `sensor03`.
  * Client cho phép chọn một hoặc nhiều mã thiết bị cần giám sát (tham số `-d`).
  * Tự động ghi dữ liệu nhận được ra file `sensor_log.csv` (hoặc `sensor_log.jsonl` với `--log-format json`).
  * Đếm số lần `GET` và tính thời gian phản hồi trung bình (kèm min/max), hiển thị sau mỗi lần GET và khi thoát chương trình.

### 4. Log minh chứng

Sensor CoAP Server:

```
CoAP Sensor Server started on port 5683
Resource: coap://localhost:5683/iot/lab/sensor01/data
Resource: coap://localhost:5683/iot/lab/sensor02/data
Resource: coap://localhost:5683/iot/lab/sensor03/data
Nhan Ctrl+C de dung server.

[20:34:41] GET /iot/lab/sensor01/data (lan thu 1) -> T=20.9 C, H=34.1 %
[20:34:44] GET /iot/lab/sensor01/data (lan thu 2) -> T=39.3 C, H=47.5 %
[20:34:47] GET /iot/lab/sensor01/data (lan thu 3) -> T=37.5 C, H=60.6 %
[20:34:50] GET /iot/lab/sensor01/data (lan thu 4) -> T=21.4 C, H=46.8 %
[20:34:53] GET /iot/lab/sensor01/data (lan thu 5) -> T=38.9 C, H=51.4 %
[20:34:56] GET /iot/lab/sensor01/data (lan thu 6) -> T=41.5 C, H=52.8 %
[20:34:59] GET /iot/lab/sensor01/data (lan thu 7) -> T=35.5 C, H=56.8 %
[20:35:02] GET /iot/lab/sensor01/data (lan thu 8) -> T=38.5 C, H=31.3 %
```

Monitoring CoAP Client:

```
[20:34:41] Received sensor data
Device: sensor01
Temperature: 20.9 C
Humidity: 34.1 %
Server timestamp: 2026-10-31T20:34:39
CANH BAO: Do am thap
[GET #1] Response time: 4.74 ms | Avg: 4.74 ms
------------------------------
[20:34:44] Received sensor data
Device: sensor01
Temperature: 39.3 C
Humidity: 47.5 %
Server timestamp: 2026-10-31T20:34:42
CANH BAO: Nhiet do cao
[GET #2] Response time: 1.38 ms | Avg: 3.06 ms
........

Exiting monitoring...
=== THONG KE ===
Tong so GET     : 10
Thanh cong      : 8
That bai        : 2
Thoi gian phan hoi trung binh: 2.81 ms (min 1.21 / max 4.74)
```
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
