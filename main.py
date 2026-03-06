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
CHALLENGE_NAME = "BLINK TWICE"
CHALLENGE_TIMEOUT = 8
IS_WINDOWS = os.name == 'nt'

# Colors (BGR)
ACCENT_COLOR = (57, 255, 20)  # Neon Green
UNKNOWN_COLOR = (0, 0, 255)   # Bright Red
BUTTON_COLOR = (0, 0, 200)    # Red for Close Button
ALERT_COLOR = (0, 165, 255)   # Orange for security warnings

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

def detect_phone_screens(img_small):
    gray = cv2.cvtColor(img_small, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 130)
    edges = cv2.dilate(edges, None, iterations=1)
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h, w = gray.shape
    frame_area = h * w
    phones = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < frame_area * 0.006 or area > frame_area * 0.75:
            continue

        rect = cv2.minAreaRect(cnt)
        _, (rw, rh), _ = rect
        if rw < 18 or rh < 18:
            continue

        long_side = max(rw, rh)
        short_side = min(rw, rh)
        if long_side < 45:
            continue

        aspect = long_side / (short_side + 1e-6)
        if aspect < 1.25 or aspect > 3.2:
            continue

        box = cv2.boxPoints(rect).astype(np.int32)
        x, y, bw, bh = cv2.boundingRect(box)
        bbox_area = float(bw * bh)
        if bbox_area <= 0:
            continue
        if bbox_area > frame_area * 0.55:
            continue
        # Ignore contours that are effectively the full frame border.
        if x <= 2 and y <= 2 and (x + bw) >= (w - 2) and (y + bh) >= (h - 2):
            continue

        fill_ratio = area / bbox_area
        if fill_ratio < 0.28:
            continue

        mask = np.zeros_like(gray, dtype=np.uint8)
        cv2.fillConvexPoly(mask, box, 255)
        mask_pixels = cv2.countNonZero(mask)
        if mask_pixels == 0:
            continue

        mean_brightness = cv2.mean(gray, mask=mask)[0]
        std_dev = cv2.meanStdDev(gray, mask=mask)[1][0][0]
        edge_pixels = cv2.countNonZero(cv2.bitwise_and(edges, edges, mask=mask))
        edge_density = edge_pixels / float(mask_pixels)

        if mean_brightness < 45:
            continue
        if std_dev < 16 and edge_density < 0.04:
            continue

        phones.append({"poly": box, "bbox": (x, y, bw, bh)})

    return phones

def face_inside_phone(face_loc, phone_regions):
    top, right, bottom, left = face_loc
    cx = (left + right) // 2
    cy = (top + bottom) // 2
    face_w = max(1, right - left)
    face_h = max(1, bottom - top)
    face_area = face_w * face_h

    for region in phone_regions:
        poly = region["poly"].astype(np.float32)
        if cv2.pointPolygonTest(poly, (float(cx), float(cy)), False) >= 0:
            return True

        x, y, w, h = region["bbox"]
        inter_left = max(left, x)
        inter_top = max(top, y)
        inter_right = min(right, x + w)
        inter_bottom = min(bottom, y + h)
        if inter_right > inter_left and inter_bottom > inter_top:
            inter_area = (inter_right - inter_left) * (inter_bottom - inter_top)
            if inter_area / float(face_area) > 0.20:
                return True

        if x <= cx <= x + w and y <= cy <= y + h:
            return True
    return False

def scale_phone_region(region, factor):
    poly = (region["poly"].astype(np.float32) * factor).astype(np.int32)
    x, y, w, h = region["bbox"]
    return {
        "poly": poly,
        "bbox": (int(x * factor), int(y * factor), int(w * factor), int(h * factor))
    }

def open_camera():
    # Keep behavior identical but add robust camera startup for Windows devices.
    preferred_indexes = [0, 1, 2] if IS_WINDOWS else [1, 0, 2]
    windows_backends = [cv2.CAP_DSHOW, cv2.CAP_ANY] if IS_WINDOWS else [cv2.CAP_ANY]

    for backend in windows_backends:
        for idx in preferred_indexes:
            cap_try = cv2.VideoCapture(idx, backend)
            if not cap_try.isOpened():
                cap_try.release()
                continue
            ok, _ = cap_try.read()
            if ok:
                return cap_try
            cap_try.release()

    # Final fallback
    return cv2.VideoCapture(0)

def point_mean(points):
    pts = np.array(points, dtype=np.float32)
    return float(np.mean(pts[:, 0])), float(np.mean(pts[:, 1]))

def eye_aspect_ratio(eye_points):
    if len(eye_points) < 6:
        return 0.0
    p = np.array(eye_points, dtype=np.float32)
    vertical_1 = np.linalg.norm(p[1] - p[5])
    vertical_2 = np.linalg.norm(p[2] - p[4])
    horizontal = np.linalg.norm(p[0] - p[3]) + 1e-6
    return float((vertical_1 + vertical_2) / (2.0 * horizontal))

def get_face_motion_metrics(landmarks):
    needed = ("left_eye", "right_eye", "nose_tip", "chin")
    if any((k not in landmarks) or (len(landmarks[k]) == 0) for k in needed):
        return None

    left_eye = landmarks["left_eye"]
    right_eye = landmarks["right_eye"]
    nose_tip = landmarks["nose_tip"]
    chin = landmarks["chin"]

    ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

    lx, ly = point_mean(left_eye)
    rx, ry = point_mean(right_eye)
    nx, ny = point_mean(nose_tip)
    eye_mid_x = (lx + rx) / 2.0
    eye_mid_y = (ly + ry) / 2.0

    face_width = np.linalg.norm(np.array(chin[0], dtype=np.float32) - np.array(chin[-1], dtype=np.float32)) + 1e-6
    yaw = (nx - eye_mid_x) / face_width
    pitch = (ny - eye_mid_y) / face_width

    return {"ear": ear, "yaw": yaw, "pitch": pitch}

def create_challenge_state():
    now_ts = datetime.now().timestamp()
    return {
        "task": CHALLENGE_NAME,
        "started": now_ts,
        "progress": 0,
        "blink_down": False,
        "baseline": None,
        "verified": False,
        "last_seen": now_ts
    }

def reset_challenge_state(state, metrics):
    now_ts = datetime.now().timestamp()
    state["task"] = CHALLENGE_NAME
    state["started"] = now_ts
    state["progress"] = 0
    state["blink_down"] = False
    state["baseline"] = {"yaw": metrics["yaw"], "pitch": metrics["pitch"]} if metrics else None
    state["last_seen"] = now_ts

def update_challenge_state(state, metrics):
    now_ts = datetime.now().timestamp()
    state["last_seen"] = now_ts

    if state["verified"]:
        return True
    if metrics is None:
        return False

    if state["baseline"] is None:
        state["baseline"] = {"yaw": metrics["yaw"], "pitch": metrics["pitch"]}

    if (now_ts - state["started"]) > CHALLENGE_TIMEOUT:
        reset_challenge_state(state, metrics)
        return False

    eye_closed = metrics["ear"] < 0.18
    if eye_closed and not state["blink_down"]:
        state["blink_down"] = True
    elif (not eye_closed) and state["blink_down"]:
        state["blink_down"] = False
        state["progress"] += 1
    if state["progress"] >= 2:
        state["verified"] = True

    return state["verified"]

# --- STEP 2: CAMERA LOOP ---
cap = open_camera()
process_frame = True 
display_data = []
phone_warning = False
phone_boxes_main = []
phone_detected = False
challenge_states = {}
liveness_text = ""

if cap.isOpened():
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

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
        phone_warning = False
        liveness_text = ""
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgP = cv2.resize(img, (0, 0), None, 0.5, 0.5)
        rgbS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        phone_regions_half = detect_phone_screens(imgP)
        phone_detected = len(phone_regions_half) > 0
        phone_boxes_main = [(region["bbox"][0] * 2, region["bbox"][1] * 2, region["bbox"][2] * 2, region["bbox"][3] * 2) for region in phone_regions_half]
        phone_regions_small = [scale_phone_region(region, 0.5) for region in phone_regions_half]
        
        faceLocs = face_recognition.face_locations(rgbS, model='hog')
        faceEncodes = face_recognition.face_encodings(rgbS, faceLocs)
        faceLandmarks = face_recognition.face_landmarks(rgbS, faceLocs)
        blocked_faces = [face_inside_phone(loc, phone_regions_small) for loc in faceLocs]
        spoof_frame = any(blocked_faces)
        phone_warning = spoof_frame
        
        display_data = []
        now_ts = datetime.now().timestamp()
        for encode, loc, is_blocked, landmarks in zip(faceEncodes, faceLocs, blocked_faces, faceLandmarks):
            dist = face_recognition.face_distance(encodeListKnown, encode)
            matchIdx = np.argmin(dist)
            
            name, color = "ACCESS DENIED", UNKNOWN_COLOR
            if is_blocked:
                name, color = "PHONE IMAGE BLOCKED", ALERT_COLOR
            elif dist[matchIdx] < 0.5:
                person_name = classNames[matchIdx]
                if person_name not in challenge_states:
                    challenge_states[person_name] = create_challenge_state()

                state = challenge_states[person_name]
                metrics = get_face_motion_metrics(landmarks)
                passed = update_challenge_state(state, metrics)
                color = ACCENT_COLOR if passed else ALERT_COLOR

                if passed:
                    name = f"{person_name} VERIFIED"
                    markPresent(person_name)
                else:
                    name = f"{person_name} | BLINK {state['progress']}/2"
                    liveness_text = f"LIVENESS: {person_name} -> BLINK TWICE ({state['progress']}/2)"
            
            top, right, bottom, left = [v * 4 for v in loc]
            display_data.append(((left, top, right - left, bottom - top), name, color))

        # Remove stale non-verified challenge sessions after face disappears.
        for person_name in list(challenge_states.keys()):
            state = challenge_states[person_name]
            if (not state["verified"]) and ((now_ts - state["last_seen"]) > 12):
                del challenge_states[person_name]

    process_frame = not process_frame 

    for x, y, w, h in phone_boxes_main:
        cv2.rectangle(img, (x, y), (x + w, y + h), ALERT_COLOR, 2)
        cv2.putText(img, "PHONE DETECTED", (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ALERT_COLOR, 2)

    if phone_detected:
        cv2.putText(img, "PHONE DETECTED ON SCREEN", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, ALERT_COLOR, 2)

    if phone_warning:
        cv2.putText(img, "SECURITY ALERT: MOBILE PHONE IMAGE DETECTED", (20, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, ALERT_COLOR, 2)

    if liveness_text:
        cv2.putText(img, liveness_text, (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, ALERT_COLOR, 2)

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
