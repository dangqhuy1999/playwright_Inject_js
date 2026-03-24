import random

class LocaleManager:
    def __init__(self):
        # Danh sách các cấu hình phổ biến để xoay vòng
        self.locales = [
            {"locale": "vi-VN", "timezone": "Asia/Ho_Chi_Minh", "geo": {"latitude": 10.7626, "longitude": 106.6602}},
            {"locale": "en-US", "timezone": "America/New_York", "geo": {"latitude": 40.7128, "longitude": -74.0060}},
            {"locale": "en-GB", "timezone": "Europe/London", "geo": {"latitude": 51.5074, "longitude": -0.1278}},
            {"locale": "ja-JP", "timezone": "Asia/Tokyo", "geo": {"latitude": 35.6895, "longitude": 139.6917}}
        ]

    def get_context_params(self, proxy_url=None):
        """
        Trả về cấu hình phù hợp. 
        Nếu có proxy, bạn có thể viết thêm logic để map đúng múi giờ của Proxy đó.
        """
        # Ở đây ta lấy ngẫu nhiên hoặc mặc định vi-VN cho masothue
        selected = self.locales[0] # Ưu tiên Việt Nam cho trang MST
        return selected

locale_helper = LocaleManager()