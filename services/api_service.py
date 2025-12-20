import requests
from config.settings import API_URL

def upload_time(payload: dict):
    try:
        resp = requests.post(API_URL, json=payload, timeout=15)
        resp.raise_for_status()
        return True, resp.json()
    except Exception as e:
        return False, str(e)
