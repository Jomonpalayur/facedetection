import cv2
import os

# Load the pre-trained Haar Cascade Classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Path to the directory containing reference photos
reference_photos_dir = "reference_photos"

# List of reference photos and their resized versions
reference_photos = []
reference_photos_resized = []

# Load reference photos and resize them
for photo in os.listdir(reference_photos_dir):
    photo_path = os.path.join(reference_photos_dir, photo)
    reference_img = cv2.imread(photo_path, cv2.IMREAD_GRAYSCALE)
    reference_photos.append(reference_img)
    reference_photos_resized.append(cv2.resize(reference_img, (30, 30)))  # Resize to match face size

# Initialize the webcam (you can also provide a video file path)
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        break

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    # Process detected faces
    for (x, y, w, h) in faces:
        # Draw a rectangle around the detected face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Resize the detected face to match reference photo size
        detected_face_resized = cv2.resize(gray[y:y+h, x:x+w], (30, 30))

        # Match the detected face with reference photos
        for i, reference_face in enumerate(reference_photos_resized):
            result = cv2.matchTemplate(detected_face_resized, reference_face, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)

            # Set a threshold for face matching
            threshold = 0.8  # Adjust this threshold as needed
            if max_val >= threshold:
                cv2.putText(frame, f"Match: {os.listdir(reference_photos_dir)[i]}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the frame with detected faces and matched file names in the camera preview
    cv2.imshow('Camera Preview with Face Detection', frame)

    # Exit the loop when the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
