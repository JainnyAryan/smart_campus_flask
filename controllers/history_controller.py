from flask import Blueprint, request, jsonify
from utils.decorators import protected_route
from utils.error_handler import handle_error
from services.history_service import HistoryService
from models.models import WalletHistoryItem
from datetime import datetime
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter


# Register the blueprint
history_bp = Blueprint('history_bp', __name__, url_prefix='/history')
db = firestore.client()


@history_bp.route('/wallets/create', methods=['POST'])
@protected_route
def create_wallet_history():
    """
    Create a wallet history entry.
    """
    data: dict = request.json
    required_fields = {"wallet_id", "user_id", "addition", "amount"}

    if not required_fields.issubset(data.keys()):
        return jsonify({"message": "Invalid input data"}), 400

    try:
        # Create WalletHistoryItem instance
        wallet_history_item = WalletHistoryItem(
            id=None,  # Firestore will generate this
            wallet_id=data['wallet_id'],
            user_id=data['user_id'],
            addition=data['addition'],
            amount=data['amount'],
            time=datetime.now()
        )

        # Use the service to add history
        added_history = HistoryService.add_wallet_history(wallet_history_item)
        return jsonify(added_history), 201
    except Exception as e:
        return handle_error(e)


@history_bp.route('/wallets/<wallet_id>', methods=['GET'])
@protected_route
def get_wallet_history(wallet_id):
    try:
        history = HistoryService.get_wallet_history(wallet_id)
        if not history:
            return jsonify({"message": "No wallet history found"}), 404
        return jsonify({"data": history}), 200
    except Exception as e:
        return handle_error(e)


@history_bp.route('/financial/drivers/<driver_id>', methods=['GET'])
@protected_route
def get_driver_financial_history(driver_id):
    try:
        history = HistoryService.get_driver_financial_history(driver_id)
        print(history)
        if not history:
            return jsonify({"message": "History not found"}), 404
        return jsonify({"data": history}), 200
    except Exception as e:
        raise e
        return handle_error(e)


@history_bp.route('/financial/deduction-history', methods=['GET'])
@protected_route
def get_deduction_history():
    try:
        history_ref = db.collection('history', 'wallets', 'entries')

        query = history_ref.where(filter=FieldFilter('addition', '==', False))
        docs = query.stream()

        history_items = []
        for doc in docs:
            history_item = doc.to_dict()
            history_items.append(history_item)

        if not history_items:
            return jsonify({"message": "No deduction history found"}), 404

        return jsonify({"data": history_items}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@history_bp.route('/wallets/<history_id>', methods=['DELETE'])
@protected_route
def delete_wallet_history_item(history_id):
    """
    Delete a specific wallet activity history entry by ID.
    """
    try:
        deleted = HistoryService.delete_wallet_history(history_id)
        if not deleted:
            return jsonify({"message": "History item not found"}), 404
        return jsonify({"message": "History item deleted successfully"}), 200
    except Exception as e:
        return handle_error(e)
