===========================================================
        ADVANCED AI FACE RECOGNITION ATTENDANCE SYSTEM
===========================================================

PROJECT OVERVIEW
----------------
This is a high-performance, AI-driven attendance management system 
built using Python. It utilizes the HOG (Histogram of Oriented 
Gradients) model for face detection and Deep Learning for 
identity recognition. The system features a custom-designed 
High-Tech HUD (Heads-Up Display) for a professional user experience.

TECHNICAL REQUIREMENTS
----------------------
- Operating System: Windows 10/11
- Python Version: 3.10 or 3.11 (Recommended)
- Internet Connection: Required for the first run to install libraries.

*** IMPORTANT INSTALLATION NOTE ***
When installing Python, you MUST check the box that says 
"Add Python to PATH" or the system will not start.

FOLDER STRUCTURE
----------------
- main.py             : The core AI engine and HUD UI script.
- master_list.csv     : Database of all students expected to be present.
- known_faces/        : Folder containing 5 pre-loaded identity photos.
- attendance_logs/    : Folder where the final Excel/CSV reports are saved.
- requirements.txt    : Technical manifest for automatic setup.
- Run_Project.bat     : One-click launcher for the entire system.

HOW TO START (ONE-CLICK METHOD)
-------------------------------
1. Unzip the "Attendance_System.zip" folder to your Desktop.
2. Double-click the "Run_Project.bat" file.
3. The system will automatically:
   - Verify your Python installation.
   - Install all required libraries (OpenCV, Face Recognition, etc.).
   - Load the 5 pre-encoded student identities.
   - Launch the Secure Scan Camera Interface.

CRITICAL TROUBLESHOOTING: C++ / DLIB ERRORS
-------------------------------------------
If the terminal shows a red error saying "Failed to build dlib" or 
"Visual Studio C++ required," follow these steps:

1. Download "Visual Studio Build Tools" (Free) from Microsoft: 
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer and check the box: 
   "Desktop development with C++".
3. Click "Install" (Wait for it to finish).
4. Restart "Run_Project.bat". The error will be gone!

HOW TO USE THE SYSTEM
---------------------
1. LIVE SCANNING: Stand in front of the camera. The HUD will lock 
   onto your face with neon green brackets and display your name.
2. REAL-TIME LOGGING: The terminal will confirm "LOGGED: Name".
3. CLOSING: Click the camera window and press 'q' on your keyboard.
4. ABSENCE REPORTING: Upon closing, the system automatically 
   identifies missing students and generates a final report.

ACCESSING THE ATTENDANCE REPORT
-------------------------------
- Go to the "attendance_logs" folder.
- Open "Attendance.csv" in Microsoft Excel or Google Sheets.

Created by: Rishav Biswas
===========================================================