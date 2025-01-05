import cv2
import numpy as np

# IP Camera stream URL
ip_camera_url = "http://192.168.45.234:8080/video"  # Replace with your IP camera's URL

# Open video capture from IP camera
video = cv2.VideoCapture(ip_camera_url)

# Desired window size
window_width = 770
window_height = 434

while True:
    ret, frame = video.read()
    if not ret:
        print("Failed to grab frame from IP camera.")
        break

    # Convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray_frame, (5, 5), 0)

    # Detect edges using Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Resize the edges image to fit the smaller window
    edges_resized = cv2.resize(edges, (window_width, window_height))

    # Display the edges image
    cv2.imshow('Edges', edges_resized)

    # Find contours from edges
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 200: 
            # Approximate the contour
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            # Determine the shape based on the number of vertices
            if len(approx) == 3:
                contour_area = cv2.contourArea(contour)
                shape_name = "Triangle"
                color = (0, 255, 0)  # Green
            elif len(approx) == 4:
                # Check if the shape is a rectangle or square
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w) / h
                contour_area = cv2.contourArea(contour)
                area = w * h
                if 0.8 <= contour_area / area <= 1.2:
                    if 0.96 <= aspect_ratio <= 1.04:
                        shape_name = "Square"
                    else:
                        shape_name = "Rectangle"
                    color = (255, 0, 0)  # Blue
                else: 
                    continue
            elif len(approx) > 4:
                # Check if the shape is a circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                circle_area = np.pi * (radius ** 2)
                contour_area = cv2.contourArea(contour)
                if 0.8 <= contour_area / circle_area <= 1.2:
                    shape_name = "Circle"
                    color = (0, 0, 255)  # Red
                else:
                    continue
        else:
            continue

        # Draw the contour and the shape name
        cv2.drawContours(frame, [approx], -1, color, 3)
        x, y = approx[0][0]  # Position for text
        cv2.putText(frame, shape_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Resize the frame to fit the smaller window
    frame_resized = cv2.resize(frame, (window_width, window_height))

    # Display the frame
    cv2.imshow('Shape Detection', frame_resized)

    if cv2.waitKey(1) == ord('q'):
        break

# Release resources
video.release()
cv2.destroyAllWindows()