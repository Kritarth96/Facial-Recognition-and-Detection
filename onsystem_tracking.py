import cv2

# ----------- Camera + Face Setup ------------
cap = cv2.VideoCapture(0)  # Your laptop webcam
cap.set(3, 1920)
cap.set(4, 1080)

KNOWN_FACE_WIDTH_CM = 15.0  # average face width
FOCAL_LENGTH = 600  # you must calibrate this value once

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
frame_center = (frame_width // 2, frame_height // 2)

# ----------- Loop ------------
try:
    cv2.namedWindow("Face Tracking (Simulation)", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Face Tracking (Simulation)", 1920, 1080)  # Match your set resolution

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw crosshair in center
        cv2.line(frame, (frame_center[0], 0), (frame_center[0], frame_height), (0, 255, 255), 1)
        cv2.line(frame, (0, frame_center[1]), (frame_width, frame_center[1]), (0, 255, 255), 1)

        if len(faces) > 0:
            (x, y, w, h) = faces[0]
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            # Calculate relative coordinates
            rel_x = face_center_x - frame_center[0]
            rel_y = frame_center[1] - face_center_y

            # Estimate distance
            distance_cm = (KNOWN_FACE_WIDTH_CM * FOCAL_LENGTH) / w
            print(f"Relative Coordinates (x, y): ({rel_x}, {rel_y}, {distance_cm:.2f} cm)")

            # Draw face box and center dot
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (face_center_x, face_center_y), 3, (0, 0, 255), -1)
            cv2.putText(frame, f"({rel_x}, {rel_y}, {int(distance_cm)}cm)", (x, y - 10),
            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 2)

            # Draw line from center to face
            cv2.line(frame, frame_center, (face_center_x, face_center_y), (255, 0, 0), 1)


        # Display
        cv2.imshow("Face Tracking (Simulation)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    cap.release()
    cv2.destroyAllWindows()