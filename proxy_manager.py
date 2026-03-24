import random
import time

class ProxyManager:
    def __init__(self):
        # Định dạng: http://username:password@host:port hoặc http://host:port
        '''Thay vì code cứng danh sách Proxy, bạn có thể tìm hiểu các thư viện/dịch vụ sau để tích hợp vào hệ thống ERP/Automation của mình:

        Bright Data / Smartproxy: Họ cung cấp các Node SDK hoặc Proxy Endpoint tự động xoay vòng (Rotation), bạn chỉ cần 1 URL duy nhất.

        Proxy Broker (Python): Nếu bạn muốn tự quét và kiểm tra proxy miễn phí (nhưng độ ổn định thấp).

        Playwright Stealth: Một plugin giúp trình duyệt "giống người" hơn nữa khi đi qua Proxy.
        '''
        self.proxies = [
            "http://kjajshvi:7h5jcegzb3z1@142.111.67.146:5611/",
            "http://kjajshvi:7h5jcegzb3z1@31.59.20.176:6754/",
            "http://kjajshvi:7h5jcegzb3z1@23.95.150.145:6114/",
            "http://kjajshvi:7h5jcegzb3z1@198.23.239.134:6540/",
            # Thêm danh sách proxy của bạn ở đây
        ]
        # Dictionary lưu { proxy_url: timestamp_bi_chan }
        self.blacklist = {}
        self.blacklist_duration = 600  # 10 phút (600 giây)

    def get_random_proxy(self):
        current_time = time.time()
        
        # Làm sạch blacklist: Loại bỏ các proxy đã hết hạn 10 phút
        self.blacklist = {
            url: ts for url, ts in self.blacklist.items() 
            if current_time - ts < self.blacklist_duration
        }

        # Lọc ra danh sách proxy còn dùng được (không nằm trong blacklist)
        available_proxies = [p for p in self.proxies if p not in self.blacklist]
        available_proxies = []
        if not available_proxies:
            print("⚠️ Tất cả Proxy đều bị Blacklist! Đang dùng tạm IP gốc...")
            return None
            
        proxy_url = random.choice(available_proxies)
        return {"server": proxy_url}

    def add_to_blacklist(self, proxy_dict):
        if proxy_dict and "server" in proxy_dict:
            proxy_url = proxy_dict["server"]
            self.blacklist[proxy_url] = time.time()
            print(f"🚫 Đã đưa vào Blacklist: {proxy_url} (Tạm nghỉ 10 phút)")

proxy_helper = ProxyManager()