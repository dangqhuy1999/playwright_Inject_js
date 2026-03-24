from fake_useragent import UserAgent
'''💡 Lưu ý quan trọng cho Server (Docker/Linux)
Thư viện fake-useragent có cơ chế cache file JSON chứa danh sách UA. Nếu bạn chạy trong Docker, hãy đảm bảo folder cache này được lưu trữ (Persistent Volume) để tránh việc mỗi lần khởi động container nó lại phải tải lại danh sách từ internet, gây chậm startup.'''
class UAManager:
    def __init__(self):
        # fallback: Dùng khi không thể kết nối server để lấy UA mới nhất
        self.ua = UserAgent(
            browsers=['chrome', 'edge'], # Chỉ lấy Chrome và Edge cho ổn định
            os=['windows', 'macos'],     # Ưu tiên hệ điều hành desktop
            min_percentage=1.0           # Chỉ lấy các bản có thị phần > 1%
        )

    def get_random_ua(self):
        try:
            # Trả về một chuỗi UA ngẫu nhiên nhưng hiện đại
            return self.ua.random
        except Exception:
            # Trường hợp lỗi, trả về 1 UA "quốc dân" để hệ thống không crash
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

ua_helper = UAManager()