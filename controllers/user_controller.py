from flask import Blueprint, request, jsonify
from utils.decorators import protected_route
from utils.error_handler import handle_error
from firebase_admin import firestore, auth
from models.models import *
from controllers.wallet_controller import get_fare_value

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')
db = firestore.client()


@user_bp.route('/all', methods=['GET'])
@protected_route
def get_all_users():
    try:
        db = firestore.client()
        users_ref = db.collection('users')
        docs = users_ref.stream()

        users = []
        for doc in docs:
            users.append(doc.to_dict())  
        if not users:
            return jsonify({"message": "No users found"}), 404
        return jsonify({"users": users}), 200
    except Exception as e:
        return handle_error(e)

# Create User


@user_bp.route('/create', methods=['POST'])
def create_user():
    data: dict = request.json
    if not set(['name', 'email', 'mobile', 'type']) <= set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400

    try:
        user_auth: auth.UserRecord = auth.create_user(
            phone_number=data['mobile'])
        user_id = user_auth.uid

        user_type = data['type']
        student = Student(data['registration_number']
                          ) if user_type == 'STUDENT' else None
        driver = Driver(data['license_number']
                        ) if user_type == 'DRIVER' else None

        user = User(
            id=user_id,
            name=data['name'],
            email=data['email'],
            mobile=data['mobile'],
            type=user_type,
            student=student,
            driver=driver
        )

        db.collection("users").document(user.id).set(user.to_dict())

        return jsonify(user.to_dict()), 201
    except Exception as e:
        return handle_error(e)

# Get User


@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user_ref = db.collection('users').document(user_id).get()
        if not user_ref.exists:
            return jsonify({"message": "User not found"}), 404
        return jsonify({"user" :user_ref.to_dict(), "fare": get_fare_value()}), 200
    except Exception as e:
        return handle_error(e)

# Update User


@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    try:
        user_ref = db.collection('users').document(user_id)
        if not user_ref.get().exists:
            return jsonify({"message": "User not found"}), 404

        user_ref.update(data)
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return handle_error(e)

# Delete User


@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_ref = db.collection('users').document(user_id)
        if not user_ref.get().exists:
            return jsonify({"message": "User not found"}), 404

        user_ref.delete()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return handle_error(e)
