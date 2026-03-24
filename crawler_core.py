import asyncio
from ua_manager import ua_helper
from proxy_manager import proxy_helper

MAX_RETRIES = 3  # Số lần thử lại tối đa cho mỗi MST

async def crawl_with_retry(mst: str, attempt: int = 1):
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
        # Tối ưu chặn tài nguyên để tăng tốc
        await page.route("**/*", handle_route)
        
        # Thử truy cập
        response = await page.goto(
            f"https://masothue.com/Search/?q={mst}", 
            wait_until="domcontentloaded",
            timeout=15000 # 15s timeout cho proxy chậm
        )

        # Kiểm tra nếu bị Bot Detector chặn (Status 403 hoặc 429)
        if response.status in [403, 429]:
            raise Exception(f"Blocked by Anti-bot (Status {response.status})")

        # Đợi selector đặc trưng của dữ liệu
        await page.wait_for_selector(".table-taxinfo, .tax-listing", timeout=5000)
        
        # Thực hiện extract (giả định dùng lại JS_EXTRACT của bạn)
        if await page.locator(".table-taxinfo").count() > 0:
            data = await page.evaluate(JS_EXTRACT)
            return {"mst": mst, "data": data, "attempts": attempt, "status": "success"}

        # Xử lý trường hợp trả về danh sách (giống code cũ của bạn)
        # ... (phần chuyển hướng link ở đây) ...

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