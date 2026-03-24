import random

class ProxyManager:
    def __init__(self):
        # Định dạng: http://username:password@host:port hoặc http://host:port
        '''Thay vì code cứng danh sách Proxy, bạn có thể tìm hiểu các thư viện/dịch vụ sau để tích hợp vào hệ thống ERP/Automation của mình:

        Bright Data / Smartproxy: Họ cung cấp các Node SDK hoặc Proxy Endpoint tự động xoay vòng (Rotation), bạn chỉ cần 1 URL duy nhất.

        Proxy Broker (Python): Nếu bạn muốn tự quét và kiểm tra proxy miễn phí (nhưng độ ổn định thấp).

        Playwright Stealth: Một plugin giúp trình duyệt "giống người" hơn nữa khi đi qua Proxy.
        '''
        self.proxies = [
            "http://proxy_user1:pass1@1.2.3.4:8080",
            "http://proxy_user2:pass2@5.6.7.8:8080",
            # Thêm danh sách proxy của bạn ở đây
        ]

    def get_random_proxy(self):
        if not self.proxies:
            return None
        proxy_url = random.choice(self.proxies)
        return {"server": proxy_url}

proxy_helper = ProxyManager()