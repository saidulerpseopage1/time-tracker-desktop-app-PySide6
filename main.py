# main.py
import sys
import os
import time
import json
import glob
import random
from datetime import datetime
import threading
import requests

# GUI (PySide6)
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QTextEdit
)
from PySide6.QtCore import QTimer, Qt

# Input listeners
from pynput import mouse, keyboard

# Screenshot
from PIL import ImageGrab

# ---------- Config ----------
from config.settings import (
    API_URL,
    DEFAULT_USER_ID,
    DEFAULT_TASK_ID,
    LOG_DIR,
    SCREENSHOT_DIR,
    INACTIVITY_THRESHOLD
)

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# ---------- Helpers ----------
from services.log_service import save_daily_log

def upload_to_api(user_id, task_id, date_str, total_seconds, inactive_seconds=0):
    """Upload payload to API."""
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


# ---------- Main UI ----------
class TimeTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker")
        self.setFixedSize(420, 360)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Status / Timer display
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 28px; color: #1e88e5;")

        self.inactive_label = QLabel("Inactive: 00:00:00")
        self.inactive_label.setAlignment(Qt.AlignCenter)
        self.inactive_label.setStyleSheet("font-size: 12px; color: #e53935;")

        # Buttons
        hbox = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_pause = QPushButton("Pause")
        self.btn_stop = QPushButton("Stop")
        self.btn_upload = QPushButton("Upload Today Logs")
        hbox.addWidget(self.btn_start)
        hbox.addWidget(self.btn_pause)
        hbox.addWidget(self.btn_stop)

        # Log viewer (simple)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFixedHeight(120)

        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.timer_label)
        self.layout.addWidget(self.inactive_label)
        self.layout.addLayout(hbox)
        self.layout.addWidget(self.btn_upload)
        self.layout.addWidget(QLabel("Logs:"))
        self.layout.addWidget(self.log_view)

        # Timer internals
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 1s tick
        self._timer.timeout.connect(self._on_tick)

        self._start_time = None
        self._accumulated = 0
        self._inactive_accumulated = 0
        self._inactive_start = None
        self.is_running = False

        # Last user activity timestamp
        self.last_activity = time.time()

        # Screenshot control
        self.next_screenshot_time = None  # epoch of next screenshot

        # Input listeners
        self._mouse_listener = None
        self._keyboard_listener = None
        self._start_input_listeners()

        # Hook events
        self.btn_start.clicked.connect(self.start)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_upload.clicked.connect(self.upload_today_logs)

        self.load_logs_to_view()

    # ---------- Screenshot Logic ----------
    def schedule_next_screenshot(self, first=False):
        """Schedule next screenshot time."""
        now = time.time()

        if first:
            delay = 10  # first screenshot after 10 seconds
        else:
            delay = random.randint(30, 120)  # random interval (max 2 mins)

        self.next_screenshot_time = now + delay
        print(f"[Screenshot] Next screenshot in {delay} sec")

    def take_screenshot(self):
        """Take screenshot and save to file."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join(SCREENSHOT_DIR, f"{timestamp}.png")
        try:
            img = ImageGrab.grab()
            img.save(filepath)
            print(f"[Screenshot] Saved: {filepath}")
        except Exception as e:
            print("Screenshot failed:", e)

    # ---------- Activity Listeners ----------
    def _start_input_listeners(self):
        def on_activity(event=None):
            now = time.time()
            if self.is_running and self._inactive_start is not None:
                added = max(0, now - self._inactive_start)
                self._inactive_accumulated += int(added)
                self._inactive_start = None
            self.last_activity = now

        def on_move(x, y): on_activity()
        def on_click(x, y, button, pressed): on_activity()
        def on_scroll(x, y, dx, dy): on_activity()
        def on_press(key): on_activity()

        try:
            self._mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
            self._keyboard_listener = keyboard.Listener(on_press=on_press)
            self._mouse_listener.daemon = True
            self._keyboard_listener.daemon = True
            self._mouse_listener.start()
            self._keyboard_listener.start()
        except Exception as e:
            print("Failed to start input listeners:", e)

    # ---------- Timer Tick ----------
    def _on_tick(self):
        """Called every second."""
        running_seconds = self._accumulated
        if self.is_running and self._start_time:
            running_seconds += int(time.time() - self._start_time)
        self.timer_label.setText(self.format_running(running_seconds))

        # Inactivity detection
        total_inactive_current = 0
        if self.is_running:
            idle = time.time() - self.last_activity
            if idle > INACTIVITY_THRESHOLD:
                if self._inactive_start is None:
                    self._inactive_start = self.last_activity + INACTIVITY_THRESHOLD
                current_inactive = int(time.time() - self._inactive_start)
            else:
                current_inactive = 0
            total_inactive_current = int(self._inactive_accumulated + current_inactive)

        self.inactive_label.setText(f"Inactive: {self.format_running(total_inactive_current)}")

        # ---------- Screenshot Logic ----------
        if self.is_running and self.next_screenshot_time is not None and self._inactive_start is None:
            if time.time() >= self.next_screenshot_time:
                threading.Thread(target=self.take_screenshot, daemon=True).start()
                self.schedule_next_screenshot(first=False)

    # ---------- Formatting ----------
    def format_running(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    # ---------- Buttons ----------
    def start(self):
        if not self.is_running:
            self._start_time = time.time()
            self.is_running = True
            self._timer.start()
            self.status_label.setText("Status: Running")

            # Schedule first screenshot
            self.schedule_next_screenshot(first=True)

    def pause(self):
        if self.is_running:
            delta = int(time.time() - self._start_time)
            self._accumulated += delta

            if self._inactive_start is not None:
                added = max(0, time.time() - self._inactive_start)
                self._inactive_accumulated += int(added)
                self._inactive_start = None

            self._start_time = None
            self.is_running = False
            self._timer.stop()
            self.status_label.setText("Status: Paused")

    def stop(self):
        if self.is_running:
            delta = int(time.time() - self._start_time)
            total = self._accumulated + delta
        else:
            total = self._accumulated

        if self._inactive_start is not None:
            added = max(0, time.time() - self._inactive_start)
            self._inactive_accumulated += int(added)
            self._inactive_start = None

        inactive_total = int(self._inactive_accumulated)

        if total > 0:
            file_path, data = save_daily_log(total, inactive_total, DEFAULT_USER_ID, DEFAULT_TASK_ID)

            self._start_time = None
            self._accumulated = 0
            self._inactive_accumulated = 0
            self.is_running = False
            self._timer.stop()
            self.timer_label.setText("00:00:00")
            self.inactive_label.setText("Inactive: 00:00:00")
            self.status_label.setText("Status: Stopped")

            QMessageBox.information(self, "Saved",
                                    f"Saved {total} seconds ({inactive_total} sec inactive)")

            threading.Thread(
                target=self._background_upload_single,
                args=(DEFAULT_USER_ID, DEFAULT_TASK_ID, total, inactive_total),
                daemon=True
            ).start()

            self.load_logs_to_view()
        else:
            QMessageBox.information(self, "No time", "No tracked time to save.")

    # ---------- Upload ----------
    def _background_upload_single(self, user_id, task_id, seconds, inactive_seconds):
        date_str = datetime.now().strftime("%Y-%m-%d")
        ok, resp = upload_to_api(user_id, task_id, date_str, seconds, inactive_seconds)
        print("Upload response:", resp)

    def upload_today_logs(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        file = os.path.join(LOG_DIR, f"{date_str}.json")
        if not os.path.exists(file):
            QMessageBox.information(self, "No logs", "No logs found.")
            return

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_seconds = data.get("total_seconds", 0)
        inactive_seconds = data.get("inactive_seconds", 0)
        confirm = QMessageBox.question(
            self,
            "Upload",
            f"Upload {total_seconds} seconds?\nInactive: {inactive_seconds}",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            threading.Thread(
                target=self._do_upload_thread,
                args=(DEFAULT_USER_ID, DEFAULT_TASK_ID, date_str, total_seconds, inactive_seconds),
                daemon=True
            ).start()

    def _do_upload_thread(self, user_id, task_id, date_str, total_seconds, inactive_seconds):
        ok, resp = upload_to_api(user_id, task_id, date_str, total_seconds, inactive_seconds)
        self._notify_main_thread("Upload Result", str(resp))

    def _notify_main_thread(self, title, msg):
        def show():
            QMessageBox.information(self, title, msg)
            self.load_logs_to_view()

        QApplication.instance().postEvent(self, _RunFunctionEvent(show))

    # ---------- Log Loader ----------
    def load_logs_to_view(self):
        entries = []
        for file in sorted(glob.glob(os.path.join(LOG_DIR, "*.json")), reverse=True):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                filename = os.path.basename(file)
                entries.append(f"{filename} → {data.get('total_seconds', 0)} sec (inactive: {data.get('inactive_seconds', 0)} sec)")
            except Exception:
                continue
        self.log_view.setPlainText("\n".join(entries))

    # ---------- Close Event ----------
    def closeEvent(self, event):
        try:
            if self._mouse_listener is not None:
                self._mouse_listener.stop()
            if self._keyboard_listener is not None:
                self._keyboard_listener.stop()
        except Exception:
            pass
        super().closeEvent(event)


# Utility event
from PySide6.QtCore import QEvent
class _RunFunctionEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, func):
        super().__init__(self.EVENT_TYPE)
        self.func = func

    def execute(self):
        try:
            self.func()
        except Exception as e:
            print("Error:", e)

def custom_event(self, event):
    if isinstance(event, _RunFunctionEvent):
        event.execute()
        return True
    return super(TimeTrackerApp, self).event(event)

TimeTrackerApp.event = custom_event


# ---------- Run App ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TimeTrackerApp()
    w.show()
    sys.exit(app.exec())
