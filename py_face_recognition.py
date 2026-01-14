import face_recognition
import cv2
import os

# 1. Load sample data and "train" the system
known_face_encodings = []
known_face_names = []

# Directory containing photos of known people
known_dir = 'known/'

for filename in os.listdir(known_dir):
    if filename.endswith((".jpg", ".png")):
        # Load the image file
        image = face_recognition.load_image_file(f"{known_dir}{filename}")

        # Get the 128-number face encoding (the unique "fingerprint")
        # [0] assumes there is only one face in the sample photo
        encoding = face_recognition.face_encodings(image)[0]

        known_face_encodings.append(encoding)
        known_face_names.append(os.path.splitext(filename)[0])

print(f"Learned {len(known_face_names)} faces: {known_face_names}")

# 2. Recognize faces in a new "unknown" photo
test_image_path = 'unknown/group_photo.jpg'
test_image = face_recognition.load_image_file(test_image_path)

# Find all faces and their encodings in the test image
face_locations = face_recognition.face_locations(test_image)
face_encodings = face_recognition.face_encodings(test_image, face_locations)

# 3. Compare and Display Results
# Convert to BGR for OpenCV display
test_image_cv = cv2.imread(test_image_path)

for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
    # Check if the face matches anyone in known_face_encodings
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    name = "Unknown"

    # Use the known face with the smallest distance to the new face
    import numpy as np
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        name = known_face_names[best_match_index]

    # Draw a box around the face
    cv2.rectangle(test_image_cv, (left, top), (right, bottom), (0, 255, 0), 2)
    # Draw a label with a name below the face
    cv2.putText(test_image_cv, name, (left, bottom + 20), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

# Show the output
cv2.imshow('Face Recognition', test_image_cv)
cv2.waitKey(0)
cv2.destroyAllWindows()
