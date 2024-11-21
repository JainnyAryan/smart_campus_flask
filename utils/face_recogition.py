from PIL import Image
import json
import numpy as np

def save_face(image: Image, uid: str):

    # Generate a unique filename using UUID
    unique_filename = str(uid) + ".jpg"
    face_filename = f"testfaces/{unique_filename}"
    image.save(face_filename)
    print(f"Face saved as {face_filename}")


def get_known_face_data():
    with open('assets/face_features.json', 'r') as f:
        features_data_from_file = json.load(f)
        features = {k: np.array(v) for k, v in features_data_from_file.items()}
        known_face_encodings = list(features.values())
        known_face_names = list(features.keys())
        return known_face_encodings, known_face_names