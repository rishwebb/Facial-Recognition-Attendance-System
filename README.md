# 🎓 Face Attendance + Auto Email System

An AI-powered attendance system that recognizes faces in real time, marks attendance automatically, detects absentees, and sends absence notification emails through Gmail.

---

## ✨ Highlights

- ✅ Real-time face recognition using webcam input
- ✅ Liveness challenge (`BLINK TWICE`) before marking present
- ✅ Basic anti-spoofing by detecting phone-screen attacks
- ✅ Automatic daily absence detection from a master list
- ✅ Automatic absentee email notifications via Gmail API
- ✅ One-click launcher for Windows (`Run_Project.bat`)

---

## 🧠 How It Works

1. Loads known faces from `/known_faces`
2. Encodes each face and starts camera scanning
3. Verifies identity + liveness challenge before attendance marking
4. Saves attendance to `/attendance_logs/Attendance.csv`
5. Marks missing names from `master_list.csv` as **Absent**
6. Sends absence emails using `email_attendance.py`

---

## 📁 Project Structure

| Path | Purpose |
|---|---|
| `main.py` | Face recognition attendance engine and live UI |
| `email_attendance.py` | Sends absentee emails using Gmail API |
| `master_list.csv` | Master student list (`Name`, `Email`) |
| `known_faces/` | Reference face images (file name = person name) |
| `attendance_logs/` | Generated attendance CSV logs |
| `Run_Project.bat` | Windows one-click setup + run script |
| `requirements.txt` | Python dependencies |

---

## 🛠 Requirements

- Windows 10/11 (recommended for `.bat` launcher)
- Python 3.10+ installed and added to `PATH`
- Webcam access
- Internet connection (for dependency install and Gmail authentication)

---

## 🚀 Quick Start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Prepare data

- Add face images to `known_faces/`
- Keep image filename as the person’s name (example: `John_Doe.jpg`)
- Ensure `master_list.csv` includes matching `Name` and `Email` fields

### 3) Run attendance system

```bash
python main.py
```

Or on Windows:

```bat
Run_Project.bat
```

### 4) Send absence emails

```bash
python email_attendance.py
```

---

## 📧 Gmail Setup (for email automation)

`email_attendance.py` expects a Google OAuth client file:

- `credentials.json` in the project root

First run opens a browser for authentication and permission grant.

---

## 📊 Output

- Attendance report: `attendance_logs/Attendance.csv`
- Columns: `Name`, `Time`, `Date`, `Status`

---

## 🧯 Troubleshooting

### `Failed to build dlib` / C++ build errors

Install **Visual Studio Build Tools** and select:

- `Desktop development with C++`

Then retry:

```bash
pip install -r requirements.txt
```

### Camera not opening

- Close other apps using the camera
- Check camera permissions in system settings
- Retry with a different USB camera/device index

---

## 👤 Author

Created by **Rishav Biswas**