from flask import Blueprint, request, jsonify
from models.models import Shuttle
from utils.decorators import protected_route
from utils.error_handler import handle_error
from firebase_admin import firestore

shuttle_bp = Blueprint('shuttle_bp', __name__, url_prefix='/shuttles')
db = firestore.client()


@shuttle_bp.route('/all', methods=['GET'])
@protected_route
def get_all_shuttles():
    try:
        db = firestore.client()
        shuttles_ref = db.collection('shuttles')
        docs = shuttles_ref.stream()

        shuttles = []
        for doc in docs:
            shuttles.append(doc.to_dict())
        if not shuttles:
            return jsonify({"message": "No shuttles found"}), 404
        return jsonify({"shuttles": shuttles}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@shuttle_bp.route('/create', methods=['POST'])
def create_shuttle():
    data = request.json
    if not set(["vehicle_number", "region_type", "lat", "lng"]) == set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400

    try:
        db_ref = db.collection('shuttles')
        update_time, doc_ref = db_ref.add({})
        doc_id = doc_ref.id
        shuttle = Shuttle(
            id=doc_id,
            vehicle_number=data["vehicle_number"],
            region_type=data["region_type"],
            lat=data["lat"],
            lng=data["lng"]
        )
        db_ref.document(doc_id).set(shuttle.to_dict())

        return jsonify(shuttle.to_dict()), 201
    except Exception as e:
        return handle_error(e)


@shuttle_bp.route('/<shuttle_id>', methods=['GET'])
def get_shuttle(shuttle_id):
    try:
        shuttle_ref = db.collection('shuttles').document(shuttle_id).get()
        if not shuttle_ref.exists:
            return jsonify({"message": "Shuttle not found"}), 404
        return jsonify(shuttle_ref.to_dict()), 200
    except Exception as e:
        return handle_error(e)


@shuttle_bp.route('/<shuttle_id>/current-driver', methods=['GET'])
@protected_route
def get_current_driver(shuttle_id):
    try:
        shuttle_ref = db.collection('shuttles').document(shuttle_id).get()
        if not shuttle_ref.exists:
            return jsonify({"message": "Shuttle not found"}), 404
        shuttle_driver_ref = shuttle_ref.get('driver')
        if shuttle_driver_ref is None:
            return jsonify({"message": f"Driver not found for shuttle {shuttle_id}"}), 404
        return jsonify({"driver": shuttle_driver_ref}), 200
    except Exception as e:
        return handle_error(e)


@shuttle_bp.route('/set-current-driver', methods=['PATCH'])
@protected_route
def update_current_driver():
    data: dict = request.json
    if set(['driver', 'shuttle_id']) != set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400
    shuttle_id = data['shuttle_id']
    driver = data['driver']
    try:
        shuttle_ref = db.collection('shuttles').document(shuttle_id)
        shuttle_doc = shuttle_ref.get()
        if not shuttle_doc.exists:
            return jsonify({"message": "Shuttle not found"}), 404
        if shuttle_doc.get('driver') is not None:
            return jsonify({"message": "Shuttle already OCCUPIED by a driver!"}), 403
        shuttle_ref.update({'driver': driver})
        return jsonify({"message": "Driver updated!"}), 200
    except Exception as e:
        return handle_error(e)


@shuttle_bp.route('/remove-driver', methods=['PATCH'])
@protected_route
def remove_current_driver():
    data: dict = request.json
    id_token : str = request.headers['Authorization'].split()[1]
    if set(['shuttle_id']) != set(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400
    shuttle_id = data['shuttle_id']
    try:
        shuttle_ref = db.collection('shuttles').document(shuttle_id)
        shuttle_doc = shuttle_ref.get()
        if not shuttle_doc.exists:
            return jsonify({"message": "Shuttle not found"}), 404
        if shuttle_doc.get('driver') is None:
            return jsonify({"message": "Shuttle already EMPTY!"}), 403
        if shuttle_doc.get('driver') is not None:
            driver_id = shuttle_doc.get('driver')['id']
            if driver_id != request.user["uid"]:
                return jsonify({"message": "The requesting driver is not as same as the current driver!"}), 403
            
        shuttle_ref.update({'driver': None})
        return jsonify({"message": "Driver removed!"}), 200
    except Exception as e:
        return handle_error(e)


@shuttle_bp.route('/<shuttle_id>', methods=['PUT'])
def update_shuttle(shuttle_id):
    data = request.json
    try:
        shuttle_ref = db.collection('shuttles').document(shuttle_id)
        if not shuttle_ref.get().exists:
            return jsonify({"message": "Shuttle not found"}), 404

        shuttle_ref.update(data)
        return jsonify({"message": "Shuttle updated successfully"}), 200
    except Exception as e:
        return handle_error(e)

# Delete Shuttle


@shuttle_bp.route('/<shuttle_id>', methods=['DELETE'])
def delete_shuttle(shuttle_id):
    try:
        shuttle_ref = db.collection('shuttles').document(shuttle_id)
        if not shuttle_ref.get().exists:
            return jsonify({"message": "Shuttle not found"}), 404

        shuttle_ref.delete()
        return jsonify({"message": "Shuttle deleted successfully"}), 200
    except Exception as e:
        return handle_error(e)
