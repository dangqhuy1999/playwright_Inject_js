import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI
from playwright.async_api import async_playwright
from typing import List

app = FastAPI()

playwright = None
browser = None


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

async def handle_route(route):
    # Chặn tất cả những thứ không cần thiết để lấy dữ liệu
    excluded_resource_types = ["image", "media", "font", "stylesheet"]
    if route.request.resource_type in excluded_resource_types:
        await route.abort()
    elif "google" in route.request.url or "doubleclick" in route.request.url:
        await route.abort()
    else:
        await route.continue_()
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
    # 1. Tạo context với cấu hình tối giản
    context = await browser.new_context(user_agent="Mozilla/5.0...")
    page = await context.new_page()

    try:
        # 2. Áp dụng chặn tài nguyên
        await page.route("**/*", handle_route)

        # 3. Sử dụng wait_until="domcontentloaded" thay vì "networkidle" (nhanh hơn rất nhiều)
        url = f"https://masothue.com/Search/?q={mst}&type=enterpriseTax&force-search=0"
        await page.goto(url, wait_until="domcontentloaded")

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

    finally:
        await page.close() # Đóng page thôi
        await context.close() # Đóng context để giải phóng ram


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