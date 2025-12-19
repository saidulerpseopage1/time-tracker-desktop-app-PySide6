import json
import os
from datetime import datetime
from config.settings import LOG_DIR

def save_daily_log(total_seconds, inactive_seconds, user_id, task_id):
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(LOG_DIR, f"{date_str}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = {"total_seconds": 0, "inactive_seconds": 0, "entries": []}

    data["total_seconds"] += total_seconds
    data["inactive_seconds"] += inactive_seconds
    data["entries"].append({
        "user_id": user_id,
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "seconds": total_seconds,
        "inactive_seconds": inactive_seconds
    })

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

    return file_path, data
