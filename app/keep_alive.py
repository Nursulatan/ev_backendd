import requests
import time

# Түз URL — бекенддин өзүңдүкү
URL = "https://ev-backendd.onrender.com"

def keep_alive():
    while True:
        try:
            res = requests.get(URL, timeout=10)
            print(f"[OK] {res.status_code} - backend alive ✅")
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(600)  # 10 мүнөт сайын (600 секунд)
        
if __name__ == "__main__":
    keep_alive()
