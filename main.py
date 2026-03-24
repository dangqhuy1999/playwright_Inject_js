import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

#local build
from ua_manager import ua_helper
from proxy_manager import proxy_helper

from fastapi import FastAPI
from playwright.async_api import async_playwright
from typing import List

app = FastAPI()


playwright = None
browser = None
MAX_RETRIES = 3  # Số lần thử lại tối đa cho mỗi MST


# =============================
# 🚀 STARTUP / SHUTDOWN
# =============================
@app.on_event("startup")
async def startup():
    global playwright, browser
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )

@app.on_event("shutdown")
async def shutdown():
    await browser.close()
    await playwright.stop()

# =============================
# 🧠 JS EXTRACT (ONLY EXTRACT)
# =============================
JS_EXTRACT = """
(() => {
    let data = {};

    data["Tên Công Ty"] = document.querySelector('h1.h1')?.innerText?.trim();

    document.querySelectorAll('.table-taxinfo tbody tr').forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 2) {
            let k = cells[0].innerText.trim();
            let v = cells[1].innerText.trim()
                .replace('Ẩn số điện thoại', '')
                .split('\\n')[0]
                .trim();
            data[k] = v;
        }
    });

    return data;
})();
"""

# =============================
# ⚡ CORE CRAWLER
# =============================


# ... các phần import giữ nguyên ...

async def handle_route(route):
    # Chặn tất cả những thứ không cần thiết để lấy dữ liệu
    excluded_resource_types = ["image", "media", "font", "stylesheet"]
    if route.request.resource_type in excluded_resource_types:
        await route.abort()
    elif "google" in route.request.url or "doubleclick" in route.request.url:
        await route.abort()
    else:
        await route.continue_()

async def crawl_one(mst: str):
    # 1. Lấy thông tin định danh ngẫu nhiên
    random_ua = ua_helper.get_random_ua()
    #random_proxy = proxy_helper.get_random_proxy()

    # 2. Khởi tạo context với cấu hình "giả lập" người dùng
    context = await browser.new_context(
        user_agent=random_ua,
        #proxy=random_proxy,
        
        locale="vi-VN",
        timezone_id="Asia/Ho_Chi_Minh",
        # Invisible info
        viewport={"width": 1920, "height": 1080}, # Dùng độ phân giải phổ biến
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False
    )
    page = await context.new_page()

    try:
        # 2. Áp dụng chặn tài nguyên
        await page.route("**/*", handle_route)

        # 3. Sử dụng wait_until="domcontentloaded" thay vì "networkidle" (nhanh hơn rất nhiều)
        url = f"https://masothue.com/Search/?q={mst}&type=enterpriseTax&force-search=0"
        response = await page.goto(
            url, 
            wait_until="domcontentloaded",
            timeout=10000 # Giới hạn 10s cho mỗi trang
        )

        # Kiểm tra nếu bị Bot Detector chặn (Status 403 hoặc 429)
        if response.status in [403, 429]:
            raise Exception(f"Blocked by Anti-bot (Status {response.status})")

        # 4. Đợi selector cụ thể, không dùng timeout bừa bãi
        # Chờ xem nó ra bảng info hay ra danh sách
        try:
            await page.wait_for_selector(".table-taxinfo, .tax-listing", timeout=5000)
        except:
            return {"error": "Timeout hoặc không tìm thấy MST"}

        # Kiểm tra nhanh bằng locator thay vì lấy toàn bộ content HTML
        if await page.locator(".table-taxinfo").count() > 0:
            return await page.evaluate(JS_EXTRACT)

        if await page.locator(".tax-listing").count() > 0:
            link = page.locator(".tax-listing h3 a").first
            href = await link.get_attribute("href")
            if href:
                # Đi thẳng đến trang chi tiết
                await page.goto("https://masothue.com" + href, wait_until="domcontentloaded")
                await page.wait_for_selector(".table-taxinfo")
                return await page.evaluate(JS_EXTRACT)

        return {"error": "no data rendered"}

    except Exception as e:
        print(f"⚠️ Lần thử {attempt} cho MST {mst} thất bại: {str(e)}")
        
        if attempt < MAX_RETRIES:
            # Đóng tài nguyên cũ trước khi thử lại
            await page.close()
            await context.close()
            
            # Nghỉ một chút trước khi đổi IP/UA mới (tránh bị dính chùm)
            await asyncio.sleep(1) 
            return await crawl_with_retry(mst, attempt + 1)
        else:
            return {"mst": mst, "error": "Max retries reached", "last_error": str(e)}

    finally:
        if not page.is_closed():
            await page.close()
        await context.close()


# =============================
# 🌐 API SINGLE
# =============================
@app.get("/crawl")
async def crawl(mst: str):
    return await crawl_one(mst)



sem = asyncio.Semaphore(5) # Chỉ cho phép xử lý tối đa 5 MST cùng lúc

async def safe_crawl(mst):
    async with sem:
        return await crawl_one(mst)


# =============================
# ⚡ API BATCH (PARALLEL)
# =============================
@app.post("/crawl-batch")
async def crawl_batch(msts: List[str]):
    tasks = [safe_crawl(mst) for mst in msts]
    return await asyncio.gather(*tasks)