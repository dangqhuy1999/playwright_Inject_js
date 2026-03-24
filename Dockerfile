# Sử dụng image Playwright chính chủ từ Microsoft (Đã có sẵn mọi thứ)
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Cài đặt trình duyệt Chromium (chỉ lấy chromium cho nhẹ)
RUN playwright install chromium

# Copy toàn bộ code vào container
COPY . .

# Chạy FastAPI bằng Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]