# 🚀 Masothue Crawler API (Playwright + FastAPI)

## 📌 Overview

API crawl thông tin doanh nghiệp từ **masothue.com** bằng Playwright (async) + FastAPI.

✔ Không dùng bookmarklet hack
✔ Không phụ thuộc JS redirect loop
✔ Chạy ổn định production
✔ Handle anti-bot cơ bản

---

## ⚙️ Tech Stack

* Python 3.11+
* FastAPI
* Playwright (async)

---

## 📦 Installation

### 1. Clone project

```bash
git clone <your-repo>
cd <your-project>
```

### 2. Tạo virtual env

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn playwright
```

### 4. Install browser

```bash
playwright install
```

---

## ▶️ Run server

```bash
uvicorn main:app --reload
```

Server chạy tại:

```
http://127.0.0.1:8000
```

---

## 🌐 API Usage

### 🔹 Crawl 1 MST

```bash
curl "http://127.0.0.1:8000/crawl?mst=0313778172"
```

### 🔹 Crawl nhiều MST

```bash
curl -X POST "http://127.0.0.1:8000/crawl-batch" ^
-H "Content-Type: application/json" ^
-d "[\"0313778172\", \"0100109106\"]"
```

---

## 📊 Response Example

```json
{
  "Tên Công Ty": "CÔNG TY TNHH ...",
  "Mã số thuế": "0313778172",
  "Địa chỉ": "...",
  "Tình trạng": "Đang hoạt động"
}
```

---

## 🧠 How it works

Crawler hoạt động theo flow:

```
1. Try direct URL:
   https://masothue.com/{mst}

2. Nếu fail → search:
   https://masothue.com/Search/?q={mst}

3. Nếu có list:
   → click result đầu tiên

4. Extract data từ:
   .table-taxinfo
```

---

## ⚠️ Important Notes

### ❗ Không dùng JS redirect loop

* `window.location.href` sẽ reset state
* Playwright không giữ state JS như browser user

---

### ❗ Không block CSS / JS

Sai:

```python
route.abort() if stylesheet
```

→ DOM không render

---

### ❗ Không tin hoàn toàn selector

Trang có thể:

* load chậm
* bị anti-bot
* render khác

→ luôn fallback bằng `page.content()`

---

## 🛠 Debug Guide

### 🔍 1. Log HTML

```python
html = await page.content()
print(html[:1000])
```

---

### 🔍 2. Check URL

```python
print(page.url)
```

---

### 🔍 3. Mở browser để debug

```python
browser = await playwright.chromium.launch(headless=False)
```

---

### 🔍 4. Screenshot khi lỗi

```python
await page.screenshot(path="debug.png")
```

---

## 🚫 Common Errors

### ❌ Timeout selector

```
waiting for ".table-taxinfo"
```

👉 Nguyên nhân:

* bị anti-bot
* DOM chưa render

👉 Fix:

* thêm `wait_for_timeout(2000)`
* check `page.content()`

---

### ❌ Trả về `null`

👉 Nguyên nhân:

* dùng JS inject + redirect
* state bị reset sau navigation

👉 Fix:

* để Playwright control flow

---

### ❌ MST mismatch

👉 Do:

* search trả nhiều kết quả
* lấy nhầm link

👉 Fix:

* verify lại:

```python
if mst_returned != mst:
```

---

## ⚡ Performance

| Mode      | Time    |
| --------- | ------- |
| Single    | ~1–2s   |
| Batch 10  | ~3–5s   |
| Batch 100 | ~10–20s |

---

## 🔥 Production Tips

### ✅ Reuse browser

Không launch browser mỗi request

---

### ✅ Limit concurrency

```python
Semaphore(5)
```

---

### ✅ Retry

```python
for i in range(3):
```

---

### ✅ Fake browser

```python
user_agent
locale
timezone
```

---

### ✅ Anti-block (advanced)

* proxy rotation
* residential IP
* stealth plugin

---

## 📌 Future Improvements

* Redis queue (job system)
* Worker service (Celery / RQ)
* Proxy pool
* Captcha bypass

---

## 🧑‍💻 Author

Built for high-performance scraping 🚀
