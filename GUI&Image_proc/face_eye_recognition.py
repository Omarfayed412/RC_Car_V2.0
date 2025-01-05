import cv2

# IP Camera stream URL
ip_camera_url = "http://192.168.45.234:8080/video"  # Replace with your IP camera's URL

video = cv2.VideoCapture(ip_camera_url)

# Creating the classifier 
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Desired window size
window_width = 770
window_height = 434

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to grab frame from IP camera.")
        break
        
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # List all the faces recognized with their positions
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)

        # Relational position of eyes to face
        roi_gray = gray_frame[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        # Uncomment the following lines if you want to detect eyes as well
        # eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex, ey, ew, eh) in eyes:
        #     cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 3)

    # Resize the frame to fit the smaller window
    frame_resized = cv2.resize(frame, (window_width, window_height))

    cv2.imshow('Detect', frame_resized)

    if cv2.waitKey(1) == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
