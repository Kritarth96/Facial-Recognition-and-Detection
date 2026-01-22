import cv2

# Initialize HOG descriptor with the default people detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Open the video file (or use 0 for the webcam)
video_path = '853889-hd_1920_1080_25fps.mp4'  # Replace with your video file
cap = cv2.VideoCapture(video_path)

# Check if the video opened successfully
if not cap.isOpened():
    print(f"Error: Cannot open video file {video_path}")
    exit()

while True:
    # Read a frame from the video
    ret, frame = cap.read()

    # If frame not read correctly, exit loop
    if not ret:
        break

    # Resize frame for faster processing (optional)
    frame = cv2.resize(frame, (800, 600))

    # Detect people using HOG + SVM
    rects, _ = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)

    # Draw rectangles around detected people
    for (x, y, w, h) in rects:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

    # Display the frame
    cv2.imshow('HOG Full Body Detection', frame)

    # Exit when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
