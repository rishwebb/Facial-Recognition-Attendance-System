import warnings
# SILENCE WARNINGS: Hides internal 'pkg_resources' and other developer notifications
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import cv2 # pyright: ignore[reportMissingImports]
import face_recognition # pyright: ignore[reportMissingImports]
import numpy as np
import os
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from datetime import datetime

# --- CONFIGURATION ---
PATH = 'known_faces'
LOG_FILE = 'attendance_logs/Attendance.csv'
MASTER_LIST = 'master_list.csv'

# Colors (BGR)
ACCENT_COLOR = (57, 255, 20)  # Neon Green
UNKNOWN_COLOR = (0, 0, 255)   # Bright Red
BUTTON_COLOR = (0, 0, 200)    # Red for Close Button

# Global flag for button click
close_system = False

# Mouse Callback Function
def handle_click(event, x, y, flags, param):
    global close_system
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check if click is within the top-right button area (e.g., width-80 to width)
        if x >= param - 80 and y <= 40:
            close_system = True

# --- STEP 1: INITIALIZE SYSTEM & RESET LOGS ---
def initialize_log():
    if not os.path.exists('attendance_logs'): 
        os.makedirs('attendance_logs')
    
    # Create fresh headers for the new session
    df = pd.DataFrame(columns=['Name', 'Time', 'Date', 'Status'])
    df.to_csv(LOG_FILE, index=False)
    print("--- System Reset: Starting a fresh attendance log ---")

initialize_log()

# Load and Encode Known Faces
images, classNames = [], []
if not os.path.exists(PATH): 
    os.makedirs(PATH)

for cl in os.listdir(PATH):
    img = cv2.imread(f'{PATH}/{cl}')
    if img is not None:
        images.append(img)
        classNames.append(os.path.splitext(cl)[0])

def findEncodings(images):
    return [face_recognition.face_encodings(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))[0] for img in images]

print("Encoding faces... please wait.")
encodeListKnown = findEncodings(images)
print(f'System Active: {len(encodeListKnown)} identities loaded.')

def markPresent(name):
    df = pd.read_csv(LOG_FILE)
    today = datetime.now().strftime('%Y-%m-%d')
    if df[(df['Name'].str.upper() == name.upper()) & (df['Date'] == today)].empty:
        tString = datetime.now().strftime('%H:%M:%S')
        new_row = pd.DataFrame([[name, tString, today, 'Present']], columns=df.columns)
        new_row.to_csv(LOG_FILE, mode='a', header=False, index=False)
        print(f"✅ LOGGED: {name}")

# --- UI DRAWING HELPERS ---
def draw_hud_ui(img, bbox, name, color):
    x, y, w, h = bbox
    rt = 20 # Length of corner lines
    
    # 1. Draw Sleek Brackets
    cv2.line(img, (x, y), (x + rt, y), color, 2)
    cv2.line(img, (x, y), (x, y + rt), color, 2)
    cv2.line(img, (x + w, y), (x + w - rt, y), color, 2)
    cv2.line(img, (x + w, y), (x + w, y + rt), color, 2)
    cv2.line(img, (x, y + h), (x + rt, y + h), color, 2)
    cv2.line(img, (x, y + h), (x, y + h - rt), color, 2)
    cv2.line(img, (x + w, y + h), (x + w - rt, y + h), color, 2)
    cv2.line(img, (x + w, y + h), (x + w, y + h - rt), color, 2)

    # 2. Semi-Transparent Name Tag
    overlay = img.copy()
    cv2.rectangle(overlay, (x, y + h), (x + w, y + h + 30), color, -1)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    
    # 3. Clean Text
    display_name = name.replace("_", " ").upper()
    cv2.putText(img, display_name, (x + 10, y + h + 22), 
                cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

# --- STEP 2: CAMERA LOOP ---
cap = cv2.VideoCapture(0)
process_frame = True 
display_data = []

# WINDOW SETUP
cv2.namedWindow('Attendance System Pro', cv2.WINDOW_NORMAL)

print('Starting Camera... Press "q" or click the RED BUTTON to quit.')

while True:
    success, img = cap.read()
    if not success: break
    
    h_main, w_main, _ = img.shape
    
    # Set mouse callback to handle clicks on the current window width
    cv2.setMouseCallback('Attendance System Pro', handle_click, param=w_main)

    # Draw Close Button in top right corner
    cv2.rectangle(img, (w_main - 80, 0), (w_main, 40), BUTTON_COLOR, -1)
    cv2.putText(img, "EXIT", (w_main - 65, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Header HUD Info
    cv2.putText(img, f"SECURE SCAN | {datetime.now().strftime('%H:%M:%S')}", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    if process_frame:
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        rgbS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        
        faceLocs = face_recognition.face_locations(rgbS, model='hog')
        faceEncodes = face_recognition.face_encodings(rgbS, faceLocs)
        
        display_data = []
        for encode, loc in zip(faceEncodes, faceLocs):
            dist = face_recognition.face_distance(encodeListKnown, encode)
            matchIdx = np.argmin(dist)
            
            name, color = "ACCESS DENIED", UNKNOWN_COLOR
            if dist[matchIdx] < 0.5:
                name = classNames[matchIdx]
                color = ACCENT_COLOR
                markPresent(name)
            
            top, right, bottom, left = [v * 4 for v in loc]
            display_data.append(((left, top, right - left, bottom - top), name, color))

    process_frame = not process_frame 

    for bbox, name, color in display_data:
        draw_hud_ui(img, bbox, name, color)

    cv2.imshow('Attendance System Pro', img)
    
    # HIT 'q' OR CLICK BUTTON TO CLOSE
    if (cv2.waitKey(1) & 0xFF == ord('q')) or close_system:
        break

# --- STEP 3: CLEANUP & FINAL REPORTS ---
cap.release()
cv2.destroyAllWindows()
print("\n[INFO] Camera Closed. Processing reports...")

if os.path.exists(MASTER_LIST):
    master_df = pd.read_csv(MASTER_LIST)
    att_df = pd.read_csv(LOG_FILE)
    today = datetime.now().strftime('%Y-%m-%d')
    present_list = att_df[att_df['Date'] == today]['Name'].str.upper().tolist()
    
    print("\n--- DAILY ABSENCE REPORT ---")
    for person in master_df['Name']:
        if person.upper() not in present_list:
            absent_row = pd.DataFrame([[person, 'N/A', today, 'Absent']], columns=att_df.columns)
            absent_row.to_csv(LOG_FILE, mode='a', header=False, index=False)
            print(f"❌ ABSENT: {person}")
    print("\nFinal report saved in attendance_logs/Attendance.csv")