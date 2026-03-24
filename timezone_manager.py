import random

class TimezoneManager:
    def __init__(self):
        # Danh sách cấu hình đồng bộ (Locale + Timezone)
        self.tz_configs = {
            "VN": {"locale": "vi-VN", "timezone": "Asia/Ho_Chi_Minh"},
            "US": {"locale": "en-US", "timezone": "America/New_York"},
            "SG": {"locale": "en-SG", "timezone": "Asia/Singapore"},
            "JP": {"locale": "ja-JP", "timezone": "Asia/Tokyo"},
            "UK": {"locale": "en-GB", "timezone": "Europe/London"}
        }

    def get_config_by_country(self, country_code="VN"):
        """Trả về cấu hình dựa trên mã quốc gia của Proxy"""
        config = self.tz_configs.get(country_code.upper(), self.tz_configs["VN"])
        return config

    def get_random_config(self):
        """Lấy ngẫu nhiên một múi giờ để giả lập nhiều người dùng khác nhau"""
        return random.choice(list(self.tz_configs.values()))

tz_helper = TimezoneManager()