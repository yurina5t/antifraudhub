import os

def get_worker_mode() -> str:
    """
    Определяет режим работы сервиса:
    - realtime: запросы по одному пользователю
    - batch: batch scoring
    """
    return os.getenv("WORKER_MODE", "realtime")
