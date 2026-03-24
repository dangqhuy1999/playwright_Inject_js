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

async def handle_route(route, request):
    if "doubleclick" in request.url:
        await route.abort()
    else:
        await route.continue_()
# =============================
# ⚡ CORE CRAWLER
# =============================


async def crawl_one(mst: str):
    context = await browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    locale="vi-VN",
    timezone_id="Asia/Ho_Chi_Minh",
    viewport={"width": 1280, "height": 800}
)
    page = await context.new_page()

    try:
        await page.route("**/*", handle_route)

        await page.goto(
            f"https://masothue.com/Search/?q={mst}&type=enterpriseTax&force-search=0"
        )

        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        html = await page.content()

        # ======================
        # 🥇 DETAIL
        # ======================
        if "table-taxinfo" in html:
            return await page.evaluate(JS_EXTRACT)

        # ======================
        # 🥈 LIST
        # ======================
        if "tax-listing" in html:
            link = page.locator(".tax-listing h3 a").first
            href = await link.get_attribute("href")

            if not href:
                return {"error": "no link"}

            await page.goto("https://masothue.com" + href)

            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(2000)

            return await page.evaluate(JS_EXTRACT)

        return {"error": "no data rendered"}

    finally:
        await context.close()


# =============================
# 🌐 API SINGLE
# =============================
@app.get("/crawl")
async def crawl(mst: str):
    return await crawl_one(mst)


# =============================
# ⚡ API BATCH (PARALLEL)
# =============================
@app.post("/crawl-batch")
async def crawl_batch(msts: List[str]):
    tasks = [crawl_one(mst) for mst in msts]
    return await asyncio.gather(*tasks)