
## 🚀 Enterprise Masothue Crawler API (Playwright + FastAPI)

Hệ thống cào dữ liệu mã số thuế (MST) hiệu suất cao, ổn định và chuyên nghiệp, được thiết kế dành cho các dự án ERP, Automation và tích hợp hệ thống lớn.

---

## 🌟 Tính năng nổi bật

- **Kiến trúc Modular**: Tách biệt hoàn toàn Proxy, User-Agent, Locale, Timezone và Geolocation.
- **Zero-Latency User-Agent**: Danh sách UA Chrome/Edge 2026 được load trực tiếp vào RAM, không độ trễ.
- **Smart Proxy Blacklist**: Tự động cách ly proxy lỗi (403/429) trong 10-15 phút, đảm bảo tỷ lệ thành công ~99%.
- **Deep Stealth Mode**: Giả lập "Digital Twin" bằng cách đồng bộ Geolocation (Lat/Lon), Timezone và Locale khớp với trình duyệt.
- **Tối ưu hiệu suất**:
  - Chặn Image, Font, Media, Google Ads → giảm tới 80% băng thông.
  - Sử dụng `domcontentloaded` + JS extraction ngay trong context để tốc độ tối đa.

---

## 🏗 Cấu trúc dự án

```text
.
├── main.py                 # FastAPI Entry point & Browser Lifecycle
├── crawler_core.py          # Logic crawl chính & Retry mechanism (Class TaxCrawler)
├── proxy_manager.py        # Quản lý Proxy + Blacklist algorithm
├── ua_manager.py           # Quản lý User-Agent (Zero Latency)
├── locale_manager.py       # Đồng bộ ngôn ngữ & Geolocation (Lat/Lon)
├── timezone_manager.py     # Đồng bộ múi giờ
├── Dockerfile              # Docker image
└── docker-compose.yml      # Triển khai production
```

## 📦 Cài đặt & Chạy (Local)

### 1. Khởi tạo môi trường

```bash
python -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
playwright install chromium
```

### 2. Chạy server phát triển

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🐳 Triển khai Production với Docker

```bash
# Build và chạy nền
docker compose up -d --build

# Xem log thời gian thực
docker logs -f robolink_tax_crawler
```

## 🌐 Hướng dẫn sử dụng API

### Crawl một mã số thuế

```http
GET /crawl?mst=0313778172
```

### Crawl hàng loạt (Batch)

```http
POST /crawl-batch
```

**Body (JSON):**
```json
["0313778172", "0101234567", "0314889102"]
```

## 🧠 Cơ chế hoạt động

- **Startup**: FastAPI khởi tạo một Browser instance duy nhất và TaxCrawler class.
- **Context Creation**: Mỗi request tạo BrowserContext mới với UA, Timezone, Locale, Geolocation riêng.
- **Resource Blocking**: Chặn hình ảnh, font, media để tăng tốc độ đáng kể.
- **Data Extraction**: Chạy JavaScript trực tiếp trong page context ngay khi domcontentloaded.
- **Auto Recovery**: Gặp lỗi proxy hoặc bị chặn → tự động blacklist và retry với danh tính mới.


## 🛠 Debug & Troubleshooting

- **Lỗi 403/429**: Website phát hiện bot → kiểm tra chất lượng proxy.
- **NoneType Error**: Kiểm tra biến crawler đã được khởi tạo trong startup event chưa.
- **Geolocation Error**: Đảm bảo truyền đủ latitude và longitude (không viết tắt).


## 🧑‍💻 Tác giả

**Huy Dang (Light)** – IT Automation Engineer

Hệ thống được tối ưu mạnh về tốc độ, độ ổn định và khả năng scale.