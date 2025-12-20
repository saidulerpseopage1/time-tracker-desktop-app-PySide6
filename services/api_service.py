import requests
from config.settings import API_URL

def upload_to_api(user_id, task_id, date_str, total_seconds, inactive_seconds=0):
    payload = {
        "user_id": user_id,
        "task_id": task_id,
        "date": date_str,
        "total_seconds": int(total_seconds),
        "inactive_seconds": int(inactive_seconds)
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=15)
        resp.raise_for_status()
        try:
            return True, resp.json()
        except Exception:
            return True, resp.text
    except Exception as e:
        return False, str(e)
