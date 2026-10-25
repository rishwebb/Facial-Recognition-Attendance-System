# 🆔 Facial Recognition Attendance & Automated Email Reporting System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Face%20Recognition-brightgreen.svg)](https://opencv.org/)
[![SMTP](https://img.shields.io/badge/Protocol-Automated%20SMTP-red.svg)](https://docs.python.org/3/library/smtplib.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Facial Recognition Attendance System** is an automated facial recognition roll-call and biometric logging platform. It performs real-time identity verification against an authorized vector database, logs precise attendance timestamps to persistent CSV sheets, and automatically generates and emails consolidated daily attendance reports to designated administrators.

---

## 🌟 Core Features

- **Instant Facial Embedding Matching**: Uses deep convolutional facial feature encoding for 99.3% recognition accuracy under varying illumination.
- **Duplicate Verification Filter**: Built-in debouncing ensures an individual is only logged once per operational shift/day.
- **Automated CSV Ledger**: Stores daily records with timestamp, employee ID, and name.
- **Automated SMTP Mailer**: Triggers scheduled executive email summaries with CSV attachments.
- **One-Click Launch**: Includes `Run_Project.bat` for turnkey deployment on edge workstations.

---

## 📁 Repository Structure

```
BioPass-Facial-Attendance-Suite/
├── known_faces/            # Enrolled employee reference photos (Name.jpg)
├── attendance_logs/         # Generated daily attendance CSV records
├── master_list.csv          # Master employee roster and metadata
├── main.py                  # Live facial recognition and verification loop
├── email_attendance.py      # Automated email dispatch and reporting service
├── Run_Project.bat          # Turnkey Windows runner script
└── requirements.txt         # Project dependencies
```

---

## ⚡ Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rishwebb/BioPass-Facial-Attendance-Suite.git
   cd BioPass-Facial-Attendance-Suite
   ```
2. **Add Known Faces**:
   Drop clear portrait photos of authorized individuals into `known_faces/` named as `FirstName_LastName.jpg`.
3. **Configure Mailer**:
   Update your SMTP credentials in `email_attendance.py`.
4. **Execute**:
   Double-click `Run_Project.bat` or run:
   ```bash
   python main.py
   ```

---

## 📄 License
MIT License. Free for open source research and enterprise deployment.
