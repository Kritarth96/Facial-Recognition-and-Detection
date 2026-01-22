import cv2
import RPi.GPIO as GPIO
import time

# ----------- Servo Setup ------------
pan_pin = 23
tilt_pin = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(pan_pin, GPIO.OUT)
GPIO.setup(tilt_pin, GPIO.OUT)

pan = GPIO.PWM(pan_pin, 50)  # 50Hz
tilt = GPIO.PWM(tilt_pin, 50)

pan.start(7.5)  # Center position
tilt.start(7.5)

pan_angle = 90
tilt_angle = 90

def clamp_angle(angle):
    return max(0, min(180, angle))

def set_servo_angle(pwm, angle):
    duty = 2.5 + (angle / 18.0)
    pwm.ChangeDutyCycle(duty)

# ----------- Camera Setup ------------

cap = cv2.VideoCapture(0)
cap.set(3, 900)
cap.set(4, 900)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
frame_center = (frame_width // 2, frame_height // 2)

# ----------- Loop ------------
prev_pan = pan_angle
prev_tilt = tilt_angle

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 4)  # Slightly reduced scaleFactor for speed

        # Draw crosshair
        cv2.line(frame, (frame_center[0], 0), (frame_center[0], frame_height), (0, 255, 255), 1)
        cv2.line(frame, (0, frame_center[1]), (frame_width, frame_center[1]), (0, 255, 255), 1)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (face_center_x, face_center_y), 3, (0, 0, 255), -1)
            cv2.line(frame, frame_center, (face_center_x, face_center_y), (255, 0, 0), 1)

            offset_x = face_center_x - frame_center[0]
            offset_y = face_center_y - frame_center[1]

            # Servo movement threshold to avoid jitter
            if abs(offset_x) > 10:
                pan_angle -= offset_x * 0.03
                pan_angle = clamp_angle(pan_angle)

            if abs(offset_y) > 10:
                tilt_angle += offset_y * 0.03
                tilt_angle = clamp_angle(tilt_angle)

            # Update only if angle changed significantly
            if abs(pan_angle - prev_pan) > 1:
                set_servo_angle(pan, pan_angle)
                prev_pan = pan_angle

            if abs(tilt_angle - prev_tilt) > 1:
                set_servo_angle(tilt, tilt_angle)
                prev_tilt = tilt_angle

        cv2.imshow("Face Tracking with Crosshair", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    cap.release()
    cv2.destroyAllWindows()
    pan.stop()
    tilt.stop()
    GPIO.cleanup()