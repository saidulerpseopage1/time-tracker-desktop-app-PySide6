# Time Tracker Desktop App (PySide6)

A desktop time tracking application built with **Python + PySide6**, featuring:

- Start, Pause, Stop tracking with real-time timer display.
- Inactivity detection (time spent idle is counted separately).
- Automatic screenshots at random intervals (max 2 minutes, first screenshot after 10 seconds).
- Optionally uploads time logs to a Laravel API.
- Logs saved locally in JSON format.

---

## Features

1. **Time Tracking**
   - Track work time with Start, Pause, Stop buttons.
   - Inactive time is excluded from screenshots.
   - Daily logs are saved automatically.

2. **Screenshot**
   - Captures screenshots while the timer is running.
   - Screenshots are skipped during inactive periods.
   - Saves screenshots to the `screenshots/` folder.

3. **Upload to API**
   - Logs can be uploaded to your Laravel backend.
   - Configurable user ID and task ID.

---

## Prerequisites

- Python >= 3.11
- Windows OS (tested)
- Recommended: Git installed

---

## Project Setup

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/time-tracker-desktop-app-PySide6.git
cd time-tracker-desktop-app-PySide6

    Create a virtual environment

python -m venv .venv

    Activate the virtual environment

    Windows (PowerShell):

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate

    Windows (CMD):

.venv\Scripts\activate.bat

    Linux / Mac:

source .venv/bin/activate

    Install dependencies

pip install -r requirements.txt

Running the App

python main.py

    Use Start to begin tracking.

    Pause to temporarily stop the timer.

    Stop to end tracking and save logs.

    Upload Today Logs to send the aggregated log to your Laravel API.

Directory Structure

time-tracker-desktop-app-PySide6/
│
├─ main.py                 # Main application code
├─ requirements.txt        # Python dependencies
├─ README.md               # Project instructions
├─ logs/                   # JSON logs of daily tracked time
├─ screenshots/            # Automatically captured screenshots
└─ .gitignore              # Ignore unnecessary files/folders

Git Configuration

Add .gitignore to avoid pushing unnecessary files:

# Python cache and env
__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual environment
.venv/

# Logs and screenshots
logs/
screenshots/

# IDE config
.vscode/
.idea/

After adding .gitignore:

git add .gitignore
git rm -r --cached .venv
git rm -r --cached logs
git rm -r --cached screenshots
git commit -m "Cleanup ignored files"
git push origin master

Creating Executable (Optional)

If you want to distribute the app without Python installed:

    Install PyInstaller:

pip install pyinstaller

    Build executable:

pyinstaller --noconfirm --onefile --windowed main.py

    Executable will be in dist/main.exe.

Notes

    Inactivity detection: Any period of inactivity (no mouse/keyboard) beyond 60 seconds will not trigger screenshots.

    Screenshot folder: All screenshots are saved in the screenshots/ folder with timestamped filenames.

    Log format: Stored in logs/YYYY-MM-DD.json, containing total seconds and inactive seconds.

Requirements

Minimal dependencies for the project (requirements.txt):

PySide6==6.10.1
PySide6_Addons==6.10.1
PySide6_Essentials==6.10.1
shiboken6==6.10.1
pynput==1.8.1
pillow==12.0.0
requests==2.32.5
pywin32==311
pywin32-ctypes==0.2.3

Author

    Saidul Islam

    Email / Contact: [your email]

License

MIT License