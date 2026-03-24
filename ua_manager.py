import random

class UAManager:
    def __init__(self):
        # Tự định nghĩa danh sách UA hiện đại nhất 2026
        # Việc này giúp loại bỏ hoàn toàn việc gọi ra internet, tăng tốc startup 100%
        self.ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Edge/133.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
        ]

    def get_random_ua(self):
        # Lấy ngẫu nhiên cực nhanh từ list trong bộ nhớ RAM
        return random.choice(self.ua_list)

ua_helper = UAManager()