import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import random
#local build
from ua_manager import ua_helper
from proxy_manager import proxy_helper
from locale_manager import locale_helper
from timezone_manager import tz_helper
from crawler_core import TaxCrawler

from fastapi import FastAPI
from playwright.async_api import async_playwright
from typing import List

app = FastAPI()

playwright = None
browser = None
crawler = None # 1. Khai báo biến global ở mức độ module
# =============================
# 🚀 STARTUP / SHUTDOWN
# =============================
@app.on_event("startup")
async def startup():
    global playwright, browser, crawler
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled"]
    )
    # CHỈ khởi tạo Class khi browser đã "sống"
    crawler = TaxCrawler(browser, ua_helper, proxy_helper, tz_helper, locale_helper) #

@app.on_event("shutdown")
async def shutdown():
    await browser.close()
    await playwright.stop()


'''
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

async def crawl_one(mst: str, attempt: int =1):
    # 1. Lấy thông tin định danh ngẫu nhiên
    random_ua = ua_helper.get_random_ua()
    #random_proxy = proxy_helper.get_random_proxy()
    loc_params = locale_helper.get_context_params()
    # Giả sử bạn biết Proxy của mình thuộc quốc gia nào (Ví dụ: VN)
    # Nếu dùng Proxy xoay vòng toàn cầu, bạn có thể để get_random_config()
    current_config = tz_helper.get_config_by_country("VN")
    
    # 2. Khởi tạo context với cấu hình "giả lập" người dùng
    context = await browser.new_context(
        user_agent=random_ua,
        #proxy=random_proxy,
        
        locale=loc_params["locale"],
        timezone_id=current_config["timezone"],
        geolocation=loc_params["geo"],
        permissions=["geolocation"], # Cho phép web check vị trí nếu cần
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

        # Nếu bị chặn bởi Server (Anti-bot)
        if response.status in [403, 429]:
            proxy_helper.add_to_blacklist(current_proxy) # Chặn ngay proxy này
            raise Exception(f"Bị chặn bởi Anti-bot: {response.status}")

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
        # Nếu lỗi do Proxy chết (Connection Error, Timeout)
        if "timeout" in str(e).lower() or "connection" in str(e).lower():
            proxy_helper.add_to_blacklist(current_proxy)

        if attempt < MAX_RETRIES:
            await page.close()
            await context.close()
            return await crawl_with_retry(mst, attempt + 1)
        
        return {"status": "failed", "error": str(e)}
    finally:
        if not page.is_closed():
            await page.close()
        await context.close()
'''

# =============================
# 🌐 API SINGLE
# =============================
@app.get("/crawl")
async def crawl(mst: str):
    return await crawler.crawl_with_retry(mst)



sem = asyncio.Semaphore(5) # Chỉ cho phép xử lý tối đa 5 MST cùng lúc

async def safe_crawl(mst):
    async with sem:
        return await crawler.crawl_with_retry(mst)


# =============================
# ⚡ API BATCH (PARALLEL)
# =============================
@app.post("/crawl-batch")
async def crawl_batch(msts: List[str]):
    tasks = [safe_crawl(mst) for mst in msts]
    return await asyncio.gather(*tasks)