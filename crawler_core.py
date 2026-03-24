import asyncio

class TaxCrawler:
    def __init__(self, browser, ua_helper, proxy_helper, tz_helper, locale_helper): #
        self.browser = browser
        self.ua_helper = ua_helper
        self.proxy_helper = proxy_helper
        self.tz_helper = tz_helper
        self.locale_helper = locale_helper
        self.max_retries = 3
        # =============================
        # 🧠 JS EXTRACT (ONLY EXTRACT)
        # =============================
        self.JS_EXTRACT = """
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

    async def handle_route(self, route):
        # Chặn tất cả những thứ không cần thiết để lấy dữ liệu
        excluded_resource_types = ["image", "media", "font", "stylesheet"]
        if route.request.resource_type in excluded_resource_types:
            await route.abort()
        elif "google" in route.request.url or "doubleclick" in route.request.url:
            await route.abort()
        else:
            await route.continue_()

    async def crawl_with_retry(self, mst: str, attempt: int = 1):
        # 1. Lấy thông tin định danh ngẫu nhiên
        random_ua = self.ua_helper.get_random_ua()
        random_proxy = self.proxy_helper.get_random_proxy()
        loc_params = self.locale_helper.get_context_params()
        # Giả sử bạn biết Proxy của mình thuộc quốc gia nào (Ví dụ: VN)
        # Nếu dùng Proxy xoay vòng toàn cầu, bạn có thể để get_random_config()
        current_config = self.tz_helper.get_config_by_country("VN")
        
        # 2. Khởi tạo context với cấu hình "giả lập" người dùng
        context = await self.browser.new_context(
            user_agent=random_ua,
            proxy=random_proxy,
            
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
            await page.route("**/*", self.handle_route)

            # 3. Sử dụng wait_until="domcontentloaded" thay vì "networkidle" (nhanh hơn rất nhiều)
            url = f"https://masothue.com/Search/?q={mst}&type=enterpriseTax&force-search=0"
            response = await page.goto(
                url, 
                wait_until="domcontentloaded",
                timeout=10000 # Giới hạn 10s cho mỗi trang
            )

            # Nếu bị chặn bởi Server (Anti-bot)
            if response.status in [403, 429]:
                self.proxy_helper.add_to_blacklist(random_proxy) # Chặn ngay proxy này
                raise Exception(f"Bị chặn bởi Anti-bot: {response.status}")

            # 4. Đợi selector cụ thể, không dùng timeout bừa bãi
            # Chờ xem nó ra bảng info hay ra danh sách
            try:
                await page.wait_for_selector(".table-taxinfo, .tax-listing", timeout=5000)
            except:
                return {"error": "Timeout hoặc không tìm thấy MST"}

            # Kiểm tra nhanh bằng locator thay vì lấy toàn bộ content HTML
            if await page.locator(".table-taxinfo").count() > 0:
                return await page.evaluate(self.JS_EXTRACT)

            if await page.locator(".tax-listing").count() > 0:
                link = page.locator(".tax-listing h3 a").first
                href = await link.get_attribute("href")
                if href:
                    # Đi thẳng đến trang chi tiết
                    await page.goto("https://masothue.com" + href, wait_until="domcontentloaded")
                    await page.wait_for_selector(".table-taxinfo")
                    return await page.evaluate(self.JS_EXTRACT)

            return {"error": "no data rendered"}

        except Exception as e:
            # Nếu lỗi do Proxy chết (Connection Error, Timeout)
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                self.proxy_helper.add_to_blacklist(random_proxy)

            if attempt < self.max_retries:
                await page.close()
                await context.close()
                return await self.crawl_with_retry(mst, attempt + 1)
            
            return {"status": "failed", "error": str(e)}
        finally:
            if not page.is_closed():
                await page.close()
            await context.close()
