from flask import Blueprint, request, jsonify
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import face_recognition
from utils.face_recogition import get_known_face_data
from utils.decorators import protected_route
from utils.error_handler import handle_error
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


# Load known face encodings and names (registration numbers)
known_face_encodings, known_face_names = get_known_face_data()

# Initialize Firestore
db = firestore.client()

face_bp = Blueprint('face_bp', __name__, url_prefix='/face')

@face_bp.route('/recognize', methods=['POST'])
@protected_route
def recognize_face():
    try:
        # Get the image data from the request
        data = request.json
        image_data = base64.b64decode(data['frame'])
        image = Image.open(BytesIO(image_data))
        

        # Rotate the image if necessary
        image = image.rotate(-90, expand=True)
        image_np = np.array(image)

        # Detect face locations and encodings
        face_locations = face_recognition.face_locations(image_np, number_of_times_to_upsample=3)
        face_encodings = face_recognition.face_encodings(image_np, face_locations, num_jitters=3)

        # Check if no face is detected
        if not face_encodings:
            print("No face not found")
            return jsonify({"student": None, "confidence": 0.0, "message" : "No face was detected!"}), 404

        # Process each detected face encoding
        for i, face_encoding in enumerate(face_encodings):
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            registration_number = known_face_names[best_match_index]
            confidence = 1 - face_distances[best_match_index]

            print(f"Detected face: {registration_number} with confidence {confidence}")

            # Query Firestore to find a user where student.registration_number matches
            users_ref = db.collection('users')
            query = users_ref.where(filter=FieldFilter('student.registration_number', '==', registration_number))
            user_docs = query.stream()

            # Check if any matching document is found
            student_data = None
            for doc in user_docs:
                student_data = doc.to_dict()
                break  # Get the first matching document

            if student_data:
                return jsonify({"student": student_data, "confidence": confidence}), 200
            else:
                return jsonify({"student": None, "confidence": confidence, "message": "Student not found in database!"}), 404

    except Exception as e:
        print(f"Error processing image: {e}")
        return handle_error(e)
