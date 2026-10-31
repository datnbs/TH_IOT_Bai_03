import argparse
import asyncio
import csv
import json
import os
import time
from datetime import datetime

import aiocoap
from aiocoap.error import Error as CoAPError


SERVER_HOST = "127.0.0.1"      
DISPLAY_HOST = "localhost"     
SERVER_PORT = 5683
URI_TEMPLATE = "coap://{host}:{port}/iot/lab/{device}/data"

DEFAULT_DEVICES = ["sensor01"]  
POLL_INTERVAL = 3.0             
TIMEOUT_SECONDS = 5.0           

TEMPERATURE_THRESHOLD = 35.0    
HUMIDITY_THRESHOLD = 40.0       

LOG_FORMAT = "csv"              
LOG_FILE = None                 

WARN_TEMPERATURE = "CANH BAO: Nhiet do cao"
WARN_HUMIDITY = "CANH BAO: Do am thap"
STATUS_NORMAL = "Trang thai: Binh thuong"

CSV_FIELDS = [
    "received_time", "device_id", "temperature", "humidity",
    "server_timestamp", "warnings", "response_ms",
]


class Stats:
    def __init__(self):
        self.total = 0
        self.success = 0
        self.failed = 0
        self.total_ms = 0.0
        self.min_ms = None
        self.max_ms = None

    def add_success(self, ms):
        self.total += 1
        self.success += 1
        self.total_ms += ms
        self.min_ms = ms if self.min_ms is None else min(self.min_ms, ms)
        self.max_ms = ms if self.max_ms is None else max(self.max_ms, ms)

    def add_failure(self):
        self.total += 1
        self.failed += 1

    @property
    def avg_ms(self):
        return self.total_ms / self.success if self.success else 0.0

    def summary(self):
        print("=== THONG KE ===")
        print(f"Tong so GET     : {self.total}")
        print(f"Thanh cong      : {self.success}")
        print(f"That bai        : {self.failed}")
        if self.success:
            print(f"Thoi gian phan hoi trung binh: {self.avg_ms:.2f} ms "
                  f"(min {self.min_ms:.2f} / max {self.max_ms:.2f})")


class DataLogger:
    def __init__(self, log_format, log_file):
        self.format = log_format
        self.path = None
        if log_format == "none":
            return
        ext = "csv" if log_format == "csv" else "jsonl"
        self.path = log_file or f"sensor_log.{ext}"
        if log_format == "csv" and (not os.path.exists(self.path)
                                    or os.path.getsize(self.path) == 0):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

    def write(self, record):
        if self.path is None:
            return
        try:
            if self.format == "csv":
                with open(self.path, "a", newline="", encoding="utf-8") as f:
                    csv.DictWriter(f, fieldnames=CSV_FIELDS).writerow(record)
            else:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as e:
            print(f"[ERROR] Khong ghi duoc file log: {e}")


def check_warnings(temperature, humidity):
    warnings = []
    if temperature > TEMPERATURE_THRESHOLD:
        warnings.append(WARN_TEMPERATURE)
    if humidity < HUMIDITY_THRESHOLD:
        warnings.append(WARN_HUMIDITY)
    return warnings


def now_hms():
    return datetime.now().strftime("%H:%M:%S")


async def poll_device(protocol, uri, device_id, stats, logger):
    """Gửi 1 GET tới cảm biến, phân tích, hiển thị, cảnh báo và ghi log."""
    request = aiocoap.Message(code=aiocoap.GET, uri=uri)  
    start = time.perf_counter()

    try:
        response = await asyncio.wait_for(
            protocol.request(request).response, timeout=TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        stats.add_failure()
        print(f"[{now_hms()}] [ERROR] Timeout: {device_id} khong phan hoi "
              f"sau {TIMEOUT_SECONDS} giay.\n{'-' * 30}")
        return
    except CoAPError as e:
        stats.add_failure()
        print(f"[{now_hms()}] [ERROR] Loi ket noi CoAP toi {device_id}: "
              f"{e.__class__.__name__}: {e}\n{'-' * 30}")
        return
    except Exception as e:
        stats.add_failure()
        print(f"[{now_hms()}] [ERROR] Khong the ket noi toi Server: "
              f"{e.__class__.__name__}: {e}\n{'-' * 30}")
        return

    elapsed_ms = (time.perf_counter() - start) * 1000

    if not response.code.is_successful():
        stats.add_failure()
        print(f"[{now_hms()}] [ERROR] Server tra ve ma {response.code} "
              f"cho {device_id} (thiet bi khong ton tai?)\n{'-' * 30}")
        return

    try:
        data = json.loads(response.payload.decode("utf-8"))
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
        recv_device_id = data["device_id"]
    except (ValueError, KeyError, TypeError) as e:
        stats.add_failure()
        print(f"[{now_hms()}] [ERROR] Payload khong dung dinh dang JSON mong doi: "
              f"{e.__class__.__name__}: {e}\n{'-' * 30}")
        return

    stats.add_success(elapsed_ms)
    received_time = now_hms()
    server_ts = data.get("timestamp", "")
    warnings = check_warnings(temperature, humidity)

    print(f"[{received_time}] Received sensor data")
    print(f"Device: {recv_device_id}")
    print(f"Temperature: {temperature} C")
    print(f"Humidity: {humidity} %")
    if server_ts:
        print(f"Server timestamp: {server_ts}")
    if warnings:
        for w in warnings:
            print(w)
    else:
        print(STATUS_NORMAL)
    print(f"[GET #{stats.total}] Response time: {elapsed_ms:.2f} ms "
          f"| Avg: {stats.avg_ms:.2f} ms")
    print("-" * 30)

    logger.write({
        "received_time": received_time,
        "device_id": recv_device_id,
        "temperature": temperature,
        "humidity": humidity,
        "server_timestamp": server_ts,
        "warnings": "; ".join(warnings),
        "response_ms": round(elapsed_ms, 2),
    })


def parse_args():
    parser = argparse.ArgumentParser(description="Monitoring CoAP Client - Bai 2")
    parser.add_argument("-d", "--device", nargs="+", default=DEFAULT_DEVICES,
                        metavar="ID",
                        help="Ma thiet bi can giam sat, vi du: -d sensor02 hoac -d sensor01 sensor03")
    parser.add_argument("--interval", type=float, default=POLL_INTERVAL,
                        help="Chu ky GET (giay)")
    parser.add_argument("--log-format", choices=["csv", "json", "none"], default=LOG_FORMAT,
                        help="Dinh dang file log")
    parser.add_argument("--log-file", default=LOG_FILE, help="Ten file log")
    return parser.parse_args()


async def main():
    args = parse_args()
    devices = args.device
    uris = {d: URI_TEMPLATE.format(host=SERVER_HOST, port=SERVER_PORT, device=d)
            for d in devices}

    stats = Stats()
    logger = DataLogger(args.log_format, args.log_file)

    print("Monitoring CoAP Client")
    for d in devices:
        display_uri = URI_TEMPLATE.format(host=DISPLAY_HOST, port=SERVER_PORT, device=d)
        print(f"Monitoring: {display_uri}")
    print(f"Interval: {args.interval}s | Timeout: {TIMEOUT_SECONDS}s")
    if logger.path:
        print(f"Log file: {logger.path}")
    print("Nhan Ctrl+C de dung.\n")

    protocol = await aiocoap.Context.create_client_context()
    try:
        while True:
            cycle_start = time.perf_counter()
            for d in devices:
                await poll_device(protocol, uris[d], d, stats, logger)
            elapsed = time.perf_counter() - cycle_start
            await asyncio.sleep(max(0.0, args.interval - elapsed))
    finally:
        # Chạy cả khi nhấn Ctrl+C (CancelledError / KeyboardInterrupt)
        print("\nExiting monitoring...")
        stats.summary()
        await protocol.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
