from datetime import datetime
from services.api_service import upload_time

class TrackerViewModel:

    def upload_single_log(self, user_id, task_id, seconds, inactive_seconds):
        payload = {
            "user_id": user_id,
            "task_id": task_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_seconds": int(seconds),
            "inactive_seconds": int(inactive_seconds)
        }
        return upload_time(payload)

    def upload_log_by_date(self, user_id, task_id, date_str, total_seconds, inactive_seconds):
        payload = {
            "user_id": user_id,
            "task_id": task_id,
            "date": date_str,
            "total_seconds": int(total_seconds),
            "inactive_seconds": int(inactive_seconds)
        }
        return upload_time(payload)
