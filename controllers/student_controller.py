from flask import Blueprint, request, jsonify
from models.models import Driver, Student, User
from utils.decorators import protected_route
from utils.error_handler import handle_error
from firebase_admin import firestore, auth

student_bp = Blueprint('student_bp', __name__, url_prefix='/students')
db = firestore.client()


@student_bp.route('/', methods=['GET'])
@protected_route
def get_all_students():
    try:
        db = firestore.client()
        students_ref = db.collection('students')
        docs = students_ref.stream()

        students = []
        for doc in docs:
            students.append(doc.to_dict())  # or create a Student object
        if not students:
            return jsonify({"message": "No students found"}), 404
        return jsonify({"students": students}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Create Student


@student_bp.route('/create', methods=['POST'])
def create_student():
    data: dict = request.json
    if not set(['name', 'email', 'mobile', 'type', 'registration_number']) <= set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400

    try:

        user_type = data['type']
        student = Student(data['registration_number'])
        user = User(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            mobile=data['mobile'],
            type=user_type,
            student=student,
            driver=None
        )

        db.collection("users").document(user.id).set(user.to_dict())

        return jsonify(user.to_dict()), 201
    except Exception as e:
        return handle_error(e)

# Get Student


@student_bp.route('/<student_id>', methods=['GET'])
def get_student(student_id):
    try:
        student_ref = db.collection('students').document(student_id).get()
        if not student_ref.exists:
            return jsonify({"message": "Student not found"}), 404
        return jsonify(student_ref.to_dict()), 200
    except Exception as e:
        return handle_error(e)

# Update Student


@student_bp.route('/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    try:
        student_ref = db.collection('students').document(student_id)
        if not student_ref.get().exists:
            return jsonify({"message": "Student not found"}), 404

        student_ref.update(data)
        return jsonify({"message": "Student updated successfully"}), 200
    except Exception as e:
        return handle_error(e)

# Delete Student


@student_bp.route('/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        student_ref = db.collection('students').document(student_id)
        if not student_ref.get().exists:
            return jsonify({"message": "Student not found"}), 404

        student_ref.delete()
        return jsonify({"message": "Student deleted successfully"}), 200
    except Exception as e:
        return handle_error(e)
