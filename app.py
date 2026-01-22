from flask import Flask, render_template, Response, request, jsonify, redirect, url_for, send_from_directory, session
import cv2
import face_recognition as fr
import numpy as np
import os
from waitress import serve
import threading
import mysql.connector
import bcrypt
from functools import wraps
import json
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = '##96EE30'

# MySQL config
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '##96Ee30',
    'database': 'CAPSTONE'
}

SAVE_DIR = r"C:\Users\krita\CapStone\face_recognition_app\static\faces"
RECOGNITION_LOG_FILE = r"C:\Users\krita\CapStone\face_recognition_app\recognition_log.json"

known_face_encodings = []
known_face_names = []
face_recognition_log = {}  # Track face recognition events
KNOWN_FACE_WIDTH_CM = 15.0  # average face width
FOCAL_LENGTH = 600  # you must calibrate this value once

def load_recognition_log():
    """Load face recognition log from JSON file"""
    global face_recognition_log
    try:
        if os.path.exists(RECOGNITION_LOG_FILE):
            with open(RECOGNITION_LOG_FILE, 'r') as f:
                face_recognition_log = json.load(f)
            print(f"✅ Loaded recognition log with {len(face_recognition_log)} faces")
        else:
            face_recognition_log = {}
            print("📝 No existing recognition log found, starting fresh")
    except Exception as e:
        print(f"❌ Error loading recognition log: {e}")
        face_recognition_log = {}

def save_recognition_log():
    """Save face recognition log to JSON file"""
    try:
        with open(RECOGNITION_LOG_FILE, 'w') as f:
            json.dump(face_recognition_log, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving recognition log: {e}")


def load_known_faces():
    known_face_encodings.clear()
    known_face_names.clear()
    for file in os.listdir(SAVE_DIR):
        if file.endswith((".jpg", ".png")):
            name = os.path.splitext(file)[0]
            image_path = os.path.join(SAVE_DIR, file)
            try:
                image = fr.load_image_file(image_path)
                encoding = fr.face_encodings(image)
                if encoding:
                    known_face_encodings.append(encoding[0])
                    known_face_names.append(name)
                    print(f"✅ Loaded: {name}")
                else:
                    print(f"⚠️ No face found in {file}. Skipping...")
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")

load_known_faces()
load_recognition_log()  # Load persistent recognition data
video_capture = None
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

def log_face_recognition(name):
    """Log a face recognition event with timestamp"""
    current_time = datetime.now()
    today = date.today()
    
    if name not in face_recognition_log:
        face_recognition_log[name] = {
            'count': 0,
            'last_seen': None,
            'recognitions': []
        }
    
    # Only log if it's been more than 2 seconds since last recognition of this person
    # This prevents spam logging when the same face is detected in multiple consecutive frames
    last_recognition = None
    if face_recognition_log[name]['recognitions']:
        last_recognition = datetime.fromisoformat(face_recognition_log[name]['recognitions'][-1])
    
    if last_recognition is None or (current_time - last_recognition).total_seconds() > 2:
        # Check if this is the first recognition of this person today
        was_recognized_today = any(
            datetime.fromisoformat(rec_time).date() == today 
            for rec_time in face_recognition_log[name]['recognitions']
        )
        
        face_recognition_log[name]['count'] += 1
        face_recognition_log[name]['last_seen'] = current_time.isoformat()
        face_recognition_log[name]['recognitions'].append(current_time.isoformat())
        
        # Keep only last 100 recognitions per person to prevent memory issues
        if len(face_recognition_log[name]['recognitions']) > 100:
            face_recognition_log[name]['recognitions'] = face_recognition_log[name]['recognitions'][-100:]
        
        # Save to file after each recognition
        save_recognition_log()
        
        if not was_recognized_today:
            print(f"🆕 NEW face recognized today: {name} (Unique faces today: {get_unique_faces_recognized_today()})")
        else:
            print(f"📊 Re-recognized: {name} (Total: {face_recognition_log[name]['count']})")

def get_recognitions_today(name):
    """Get count of recognitions for a person today"""
    if name not in face_recognition_log:
        return 0
    
    today = date.today()
    count = 0
    for recognition_time in face_recognition_log[name]['recognitions']:
        recognition_date = datetime.fromisoformat(recognition_time).date()
        if recognition_date == today:
            count += 1
    return count

def get_unique_faces_recognized_today():
    """Get count of unique faces recognized today (each person counted only once)"""
    today = date.today()
    unique_faces_today = set()
    
    for name, data in face_recognition_log.items():
        # Check if this person was recognized today
        for recognition_time in data['recognitions']:
            recognition_date = datetime.fromisoformat(recognition_time).date()
            if recognition_date == today:
                unique_faces_today.add(name)
                break  # Once we find one recognition for today, we don't need to check more
    
    return len(unique_faces_today)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loginid' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def gen_frames(recognize_faces=False, detect_people=False):
    global video_capture
    if video_capture is None or not video_capture.isOpened():
        print("🔵 Initializing Camera...")
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_FPS, 30)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not video_capture.isOpened():
        print("❌ Failed to open camera!")
        return

    while True:
        success, frame = video_capture.read()
        if not success or frame is None:
            print("⚠️ No frame captured, stopping feed.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if recognize_faces:
            face_locations = fr.face_locations(rgb_frame)
            face_encodings = fr.face_encodings(rgb_frame, face_locations)
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = fr.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    # Log the face recognition event
                    log_face_recognition(name)

                # Draw rectangle and name
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Calculate and draw face center
                center_x = left + (right - left) // 2
                center_y = top + (bottom - top) // 2
                cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)
                face_width_px = right - left
                if face_width_px != 0:
                    distance_cm = (KNOWN_FACE_WIDTH_CM * FOCAL_LENGTH) / face_width_px
                    cv2.putText(frame, f"{int(distance_cm)} cm", (left, bottom + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                # Print center coordinates to terminal
                print(f"{name} - Face center at: ({center_x}, {center_y}, {distance_cm:.2f} cm)")

        if detect_people:
            boxes, _ = hog.detectMultiScale(frame, winStride=(8, 8))
            for (x, y, w, h) in boxes:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.putText(frame, "Person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        loginid = request.form['loginid']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT passwords FROM logins WHERE loginids = %s", (loginid,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['passwords'].encode('utf-8')):
                session['loginid'] = loginid
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Invalid credentials.")
        except Exception as e:
            return render_template('login.html', error=f"Database error: {str(e)}")

    return render_template('login.html')

@app.route('/')
@login_required
def index():
    # Redirect to modern dashboard
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('modern_dashboard.html')

@app.route('/api/faces')
@login_required
def api_faces():
    faces = []
    for file in os.listdir(SAVE_DIR):
        if file.endswith((".jpg", ".png")):
            name = os.path.splitext(file)[0]
            
            # Get recognition data from log
            recognition_data = face_recognition_log.get(name, {
                'count': 0,
                'last_seen': None,
                'recognitions': []
            })
            
            # Check if person was recognized today (1 or 0)
            recognized_today = 1 if get_recognitions_today(name) > 0 else 0
            
            faces.append({
                "id": str(hash(name)),
                "name": name.replace("_", " "),
                "filename": file,
                "recognitionCount": recognition_data['count'],
                "lastSeen": recognition_data['last_seen'],
                "recognitionsToday": recognized_today,
                "confidence": None
            })
    return jsonify(faces)

@app.route('/api/recognition_stats')
@login_required
def recognition_stats():
    """Get current recognition statistics"""
    # Count unique faces recognized today (each person counted only once)
    unique_faces_today = get_unique_faces_recognized_today()
    
    # Count total faces from directory
    total_faces = 0
    if os.path.exists(SAVE_DIR):
        total_faces = len([f for f in os.listdir(SAVE_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))])
    
    # Debug: Show which faces were recognized today
    recognized_names = []
    if face_recognition_log:
        today = date.today()
        for name, data in face_recognition_log.items():
            for recognition_time in data['recognitions']:
                recognition_date = datetime.fromisoformat(recognition_time).date()
                if recognition_date == today:
                    recognized_names.append(name)
                    break
    
    return jsonify({
        'total_faces': total_faces,
        'recognized_today': unique_faces_today,
        'active_recognitions': len(face_recognition_log),
        'recognized_names_today': recognized_names,  # For debugging
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/save_log', methods=['POST'])
@login_required
def save_log():
    """Manually save recognition log"""
    save_recognition_log()
    return jsonify({"message": "Recognition log saved", "faces_logged": len(face_recognition_log)})

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/video_feed')
@login_required
def video_feed():
    recognize_faces = request.args.get('recognize_faces') == '1'
    detect_people = request.args.get('detect_people') == '1'
    return Response(gen_frames(recognize_faces, detect_people), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera', methods=['POST'])
@login_required
def stop_camera():
    global video_capture
    if video_capture is not None and video_capture.isOpened():
        video_capture.release()
        print("🔴 Camera Stopped")
    video_capture = None
    return jsonify({"message": "Camera stopped"})

@app.route('/upload', methods=['POST'])
@login_required
def upload_face():
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400
    file = request.files['file']
    name = request.form.get("name", "").strip().replace(" ", "_")

    if file.filename == '' or name == '':
        return jsonify({"message": "Missing name or file"}), 400

    if file and file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        save_path = os.path.join(SAVE_DIR, f"{name}.jpg")
        file.save(save_path)
        load_known_faces()
        return jsonify({"message": f"Face for {name.replace('_', ' ')} uploaded successfully!"}), 200
    else:
        return jsonify({"message": "Invalid file format. Please upload JPG or PNG!"}), 400

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == '__main__':
    # Enable debug mode for development
    app.config['DEBUG'] = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    print("Starting Flask Development Server with auto-reload...")
    print("🔥 Debug mode enabled - Files will auto-reload on changes!")
    print("📁 Templates will auto-reload on changes!")
    print("🌐 Server running at: http://localhost:8080")
    
    # Use Flask's built-in development server for auto-reload
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=True)
