import requests
import os, time, requests

URL = os.getenv("KEEPALIVE_URL", "https://ev-backendd.onrender.com")  # домениң туура экенин текшер


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
