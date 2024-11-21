from flask import Blueprint, request, jsonify
from models.models import *
from utils.error_handler import handle_error
from firebase_admin import firestore
from utils.decorators import protected_route
from google.cloud.firestore_v1.base_query import FieldFilter

driver_bp = Blueprint('driver_bp', __name__, url_prefix='/drivers')
db = firestore.client()


@driver_bp.route('/all', methods=['GET'])
@protected_route
def get_all_drivers():
    try:
        db = firestore.client()
        users_ref = db.collection('users')
        query_ref = users_ref.where(
            filter=FieldFilter("type", "==", "DRIVER"))
        docs = query_ref.stream()

        drivers = []
        for doc in docs:
            drivers.append(doc.to_dict())  # or create a Driver object
        if not drivers:
            return jsonify({"message": "No drivers found"}), 404
        return jsonify({"drivers": drivers}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

# Create Driver


@driver_bp.route('/create', methods=['POST'])
@protected_route
def create_driver():
    data = request.json
    if not set(['name', 'email', 'phone', 'type', 'license_number']) == set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400

    driver = User(id=data["id"], name=data["name"], email=data["email"], mobile=data["mobile"],
                  type="DRIVER", driver=Driver(license_number=data["license_number"]))

    try:
        db.collection('users').document(driver.id).set(driver.to_dict())
        return jsonify(driver.to_dict()), 201
    except Exception as e:
        return handle_error(e)

# Get Driver


@driver_bp.route('/<driver_id>', methods=['GET'])
@protected_route
def get_driver(driver_id):
    try:
        driver_ref = db.collection('drivers').document(driver_id).get()
        if not driver_ref.exists:
            return jsonify({"message": "Driver not found"}), 404
        return jsonify(driver_ref.to_dict()), 200
    except Exception as e:
        return handle_error(e)


@driver_bp.route('/<driver_id>/check-assignment', methods=['GET'])
def check_driver_assignment(driver_id):
    try:
        # First, check if the driver exists
        driver_ref = db.collection('users').document(driver_id)
        driver = driver_ref.get()
        
        if not driver.exists:
            return jsonify({
                "error": "Driver not found",
                "message": f"No driver found with ID: {driver_id}"
            }), 404

        # Proceed to check if the driver is assigned to any active shuttle
        shuttles_ref = db.collection('shuttles')
        print(f"Checking assignment for driver_id: {driver_id}")

        query = shuttles_ref.where('driver.id', '==', driver_id).limit(1)
        results = list(query.stream())

        if results:
            shuttle = results[0]
            shuttle_data = shuttle.to_dict()
            print(f"Assigned shuttle vehicle number: {shuttle_data['vehicle_number']}")
            return jsonify({
                "assigned": True,
                "shuttle": shuttle_data
            }), 200

        # If no shuttle assignment found for the driver
        return jsonify({
            "assigned": False,
            "shuttle": None,
            "message": "Driver is not assigned to any active shuttle."
        }), 200
    except Exception as e:
        return handle_error(e)



# Update Driver


@driver_bp.route('/<driver_id>', methods=['PUT'])
@protected_route
def update_driver(driver_id):
    data = request.json
    try:
        driver_ref = db.collection('drivers').document(driver_id)
        if not driver_ref.get().exists:
            return jsonify({"message": "Driver not found"}), 404

        driver_ref.update(data)
        return jsonify({"message": "Driver updated successfully"}), 200
    except Exception as e:
        return handle_error(e)

# Delete Driver


@driver_bp.route('/<driver_id>', methods=['DELETE'])
@protected_route
def delete_driver(driver_id):
    try:
        driver_ref = db.collection('drivers').document(driver_id)
        if not driver_ref.get().exists:
            return jsonify({"message": "Driver not found"}), 404

        driver_ref.delete()
        return jsonify({"message": "Driver deleted successfully"}), 200
    except Exception as e:
        return handle_error(e)
